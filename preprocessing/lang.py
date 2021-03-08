import fasttext


def detect_language(model, text):
    pred = model.predict(text, k=1)
    lang = pred[0][0].replace("__label__", "")
    return lang


def main():
    model = fasttext.load_model("lid.176.ftz")

    detect_language(model, "Heute ist Sonntag und die Sonne scheint.")
    detect_language(model, "Today is Sunday and the sun shines.")
    detect_language(model, "Hoy es domingo y brilla el sol.")


if __name__ == "__main__":
    main()

