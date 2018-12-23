from learning.trainer import Trainer

def analyze_image(image):
    discriminator = Trainer.load_model(userconfig.model_path)[0]
