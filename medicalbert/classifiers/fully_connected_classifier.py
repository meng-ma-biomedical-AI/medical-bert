import json, logging, os, torch
import pandas as pd
from tqdm import trange, tqdm
from statistics import mean
from torch import nn

class Network(nn.Module):

    def __init__(self, vocab_size, embedding_dim, context_size):
        super(Network, self).__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.linear1 = nn.Linear(context_size * embedding_dim, 128)
        self.linear2 = nn.Linear(128, vocab_size)

    def forward(self, inputs):
        embeds = self.embeddings(inputs).view((1, -1))
        out = F.relu(self.linear1(embeds))
        out = self.linear2(out)
        log_probs = F.log_softmax(out, dim=1)
        return log_probs

def save(summary, logits, labels, path, name):
    path = os.path.join(path, name)
    if not os.path.exists(path):
        os.makedirs(path)
    json.dump(summary, open(os.path.join(path, "summary.json"), 'w'))

    first_logit = pd.Series(logits[:, 0])
    second_logit = pd.Series(logits[:, 1])
    labels = labels

    frame = {'0': first_logit, '1': second_logit, 'label': labels}

    pd.DataFrame(frame).to_csv(os.path.join(path, "output.csv"))


class FullyConnectedClassifier:
    def __init__(self, config):
        self.config = config
        self.model = Network


        bs = self.config['train_batch_size'] //self.config['gradient_accumulation_steps']
        num_steps = int(self.config['num_train_examples'] / bs /
                        self.config['gradient_accumulation_steps']) * self.config['epochs']

        logging.info("{} optimisation steps".format(num_steps))
        optimizer_grouped_parameters = [
            {'params': self.model.parameters(), 'lr': self.config['learning_rate']}
        ]

        self.optimizer = torch.optim.Adam(self.model.parameters(), self.config['learning_rate'])

        self.epochs = 0

    def train(self, datareader):
        device = torch.device(self.config['device'])
        self.model.train()
        self.model.to(device)

        batch_losses = []

        for _ in trange(self.epochs, int(self.config['epochs']), desc="Epoch"):
            epoch_loss = 0
            num_steps = 0
            batche = []
            epoch_loss = []
            with tqdm(datareader.get_train(), desc="Iteration") as t:
                for step, batch in enumerate(t):

                    batch = tuple(t.to(device) for t in batch)
                    labels, features = batch

                    outputs = self.model(features, labels=labels)

                    loss = outputs[0]

                    # Statistics
                    batche.append(loss.item())

                    loss = loss / self.config['gradient_accumulation_steps']

                    loss.backward()

                    if (step + 1) % self.config['gradient_accumulation_steps'] == 0:
                        batch_losses.append(mean(batche))
                        epoch_loss.append(mean(batche))
                        # Update the model gradients
                        self.optimizer.step()
                        self.optimizer.zero_grad()

            print("EPOCH LOSS: {}\n".format(mean(epoch_loss)))
            epoch_loss = []
            with open(os.path.join(self.config['output_dir'], self.config['experiment_name'], "batch_loss.csv"), "a") as f:
                for loss in batch_losses:
                    f.write("{}\n".format(loss))
                batch_losses = []  # reset it.

            # save a checkpoint here
            self.save()

            self.epochs = self.epochs+1

    def set_eval_mode(self, device):
        self.model.eval()
        self.model.to(device)


    def save(self):
        checkpoint = {
            'epoch': self.epochs + 1,
            'bert_dict': self.model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }
        # Make the output directory structure if it doesnt exist
        if not os.path.exists(os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints")):
            os.makedirs(os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints"))

        torch.save(checkpoint, os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints",
                                            str(self.epochs)))

        logging.info("Saved model")

    def load_from_checkpoint(self):

        if 'load_from_checkpoint' in self.config:
            file_path = os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints", self.config['load_from_checkpoint'])
            checkpoint = torch.load(file_path)
            self.epochs = checkpoint['epoch']
            self.model.load_state_dict(checkpoint['bert_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])

            # work around - for some reason reloading an optimizer that worked with CUDA tensors
            # causes an error - see https://github.com/pytorch/pytorch/issues/2830
            for state in self.optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.cuda()

    def load_from_checkpoint(self, checkpoint_file):

        if 1==1:
            file_path = os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints", checkpoint_file)
            checkpoint = torch.load(file_path)
            self.epochs = checkpoint['epoch']
            self.model.load_state_dict(checkpoint['bert_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])

            # work around - for some reason reloading an optimizer that worked with CUDA tensors
            # causes an error - see https://github.com/pytorch/pytorch/issues/2830
            for state in self.optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.cuda()