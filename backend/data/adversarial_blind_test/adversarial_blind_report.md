Dataset:
1000 samples
500 human
500 bot

Model:
ml-v3
Random Forest

Accuracy:
0.4620

Precision:
0.4354

Recall:
0.2560

F1:
0.3224

ROC-AUC:
0.3362

Human false-positive rate:
0.3320

Bot false-negative rate:
0.7440

Human-mimic bot false-negative rate:
1.0000

ALLOW:
58.6%

CAPTCHA:
20.1%

BLOCK:
21.3%

Most important weakness discovered:
The Human-Mimic and Adversarial-Mixed bots completely exploit the model's reliance on simplistic activity thresholds rather than true continuous behavior modeling.
