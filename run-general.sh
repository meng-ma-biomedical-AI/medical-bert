python medicalbert/ --experiment_name meanpool-bert-uncase-lr5e5B16-12-layers --train --eval --target readm_30d --classifier bert-mean-pool --learning_rate 0.000005 --num_layers 12 --epochs 5;
python medicalbert/ --experiment_name meanpool-bert-uncase-lr5e5B16-10-layers --train --eval --target readm_30d --classifier bert-mean-pool --learning_rate 0.000005 --num_layers 10 --epochs 5;
python medicalbert/ --experiment_name meanpool-bert-uncase-lr5e5B16-8-layers --train --eval --target readm_30d --classifier bert-mean-pool --learning_rate 0.000005 --num_layers 8 --epochs 5;
python medicalbert/ --experiment_name meanpool-bert-uncase-lr5e5B16-6-layers --train --eval --target readm_30d --classifier bert-mean-pool --learning_rate 0.000005 --num_layers 6 --epochs 5;
python medicalbert/ --experiment_name meanpool-bert-uncase-lr5e5B16-4-layers --train --eval --target readm_30d --classifier bert-mean-pool --learning_rate 0.000005 --num_layers 4 --epochs 5;
python medicalbert/ --experiment_name meanpool-bert-uncase-lr5e5B16-2-layers --train --eval --target readm_30d --classifier bert-mean-pool --learning_rate 0.000005 --num_layers 2 --epochs 5;
