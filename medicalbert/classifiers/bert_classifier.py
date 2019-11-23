import logging, os, torch
from transformers import AdamW
from transformers import WarmupLinearSchedule as get_linear_schedule_with_warmup

from classifiers.bert_model import BertForSequenceClassification

class BertRandomClassifier:
    def __init__(self, config):
        self.config = config
        pretrained = BertForSequenceClassification.from_pretrained(self.config['pretrained_model'])

        logging.warning("We are re-initialising the weights to random!")
        self.model = BertForSequenceClassification(pretrained.config)

        # To reproduce BertAdam specific behavior set correct_bias=False
        self.optimizer = AdamW(self.model.parameters(), lr=self.config['learning_rate'], correct_bias=False)

        # PyTorch scheduler
        num_steps = int(self.config['num_train_examples'] / self.config['train_batch_size'] /
                        self.config['gradient_accumulation_steps']) * \
                    self.config['epochs']

        warmup_proportion = num_steps * self.config['warmup_proportion']

        self.scheduler = get_linear_schedule_with_warmup(self.optimizer,
                                                         warmup_steps=warmup_proportion,
                                                         t_total=num_steps)
        self.epochs = 0

    def forward_pass(self, input_batch, labels):
        return self.model(input_batch, labels=labels)

    def set_train_mode(self, device):
        self.model.train()
        self.model.to(device)

    def set_eval_mode(self, device):
        self.model.eval()
        self.model.to(device)

    def model_params(self):
        return self.model.params

    def update_gradients(self):
        self.optimizer.step()
        self.scheduler.step()
        self.optimizer.zero_grad()

    def save(self):
        checkpoint = {
            'epoch': self.epochs + 1,
            'bert_dict': self.model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'scheduler': self.scheduler.state_dict()
        }
        # Make the output directory structure if it doesnt exist
        if not os.path.exists(os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints")):
            os.makedirs(os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints"))

        torch.save(checkpoint, os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints", str(self.epochs)))

        logging.info("Saved model")

    def load_from_checkpoint(self):

        if 'load_from_checkpoint' in self.config:
            file_path = os.path.join(self.config['output_dir'], self.config['experiment_name'], "checkpoints", self.config['load_from_checkpoint'])
            checkpoint = torch.load(file_path)
            self.epochs = checkpoint['epoch']
            self.model.load_state_dict(checkpoint['bert_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            self.scheduler.load_state_dict(checkpoint['scheduler'])

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
            self.scheduler.load_state_dict(checkpoint['scheduler'])

            # work around - for some reason reloading an optimizer that worked with CUDA tensors
            # causes an error - see https://github.com/pytorch/pytorch/issues/2830
            for state in self.optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.cuda()


class BertGeneralClassifier:
    def __init__(self, config):
        self.config = config
        self.model = BertForSequenceClassification.from_pretrained(self.config['pretrained_model'])

        # To reproduce BertAdam specific behavior set correct_bias=False
        self.optimizer = AdamW(self.model.parameters(), lr=self.config['learning_rate'], correct_bias=False)

        # PyTorch scheduler
        num_steps = int(self.config['num_train_examples'] / self.config['train_batch_size'] /
                         self.config['gradient_accumulation_steps']) * \
                                   self.config['epochs']

        warmup_proportion = num_steps *self.config['warmup_proportion']

        self.scheduler = get_linear_schedule_with_warmup(self.optimizer,
                                                         warmup_steps=warmup_proportion,
                                                         t_total=num_steps)
        self.epochs = 0

    def forward_pass(self, input_batch, labels):
        return self.model(input_batch, labels=labels)

    def set_train_mode(self, device):
        self.model.train()
        self.model.to(device)

    def set_eval_mode(self, device):
        self.model.eval()
        self.model.to(device)

    def model_params(self):
        return self.model.params

    def update_gradients(self):
        self.optimizer.step()
        self.scheduler.step()
        self.optimizer.zero_grad()

    def save(self):
        checkpoint = {
            'epoch': self.epochs + 1,
            'bert_dict': self.model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'scheduler': self.scheduler.state_dict()
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
            self.scheduler.load_state_dict(checkpoint['scheduler'])

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
            self.scheduler.load_state_dict(checkpoint['scheduler'])

            # work around - for some reason reloading an optimizer that worked with CUDA tensors
            # causes an error - see https://github.com/pytorch/pytorch/issues/2830
            for state in self.optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.cuda()