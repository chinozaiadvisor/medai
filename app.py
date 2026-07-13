from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── Model yuklash ───────────────────────────────────────────────────────────
model = None
class_names = []

try:
    import torch
    import torch.nn as nn
    from torchvision import transforms, models
    from torchvision.models import ResNet18_Weights
    from PIL import Image

    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'blood_group_model.pth')

    if os.path.exists(MODEL_PATH):
        checkpoint  = torch.load(MODEL_PATH, map_location='cpu')
        class_names = checkpoint.get('class_names', [])

        m = models.resnet18(weights=None)
        m.fc = nn.Linear(m.fc.in_features, len(class_names))
        m.load_state_dict(checkpoint['model_state_dict'])
        m.eval()
        model = m
        print(f"✅ Model yuklandi — sinflar: {class_names}")
    else:
        print("⚠  Model topilmadi. Avval train.py ni ishga tushiring.")

except ImportError as e:
    print(f"⚠  Import xatosi: {e}")


# ─── Transform ───────────────────────────────────────────────────────────────
def get_transform():
    from torchvision import transforms
    return transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.Grayscale(num_output_channels=3),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    # --- DEBUG LOG ---
    print(f"\n--- /predict so'rovi ---")
    print(f"content_type : {request.content_type}")
    print(f"files keys   : {list(request.files.keys())}")
    print(f"form keys    : {list(request.form.keys())}")

    if 'file' not in request.files:
        msg = f"'file' topilmadi. Kelgan kalitlar: {list(request.files.keys())}"
        print(f"400: {msg}")
        return jsonify({'error': msg}), 400

    file = request.files['file']
    print(f"filename     : '{file.filename}'")

    if file.filename == '':
        return jsonify({'error': 'Fayl nomi bo\'sh'}), 400

    allowed = {'png', 'jpg', 'jpeg', 'bmp', 'wsq', 'tif', 'tiff'}
    if '.' not in file.filename:
        return jsonify({'error': 'Fayl kengaytmasi yo\'q'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower()
    print(f"extension    : '{ext}'")

    if ext not in allowed:
        return jsonify({'error': f'Format qo\'llanilmaydi: .{ext}'}), 400

    if model is None:
        return jsonify({'error': 'Model yuklanmagan. train.py ni ishga tushiring.'}), 503

    try:
        from PIL import Image
        import torch

        img = Image.open(file.stream).convert('RGB')

        # Kvadrat kesish (center crop)
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top  = (h - side) // 2
        img  = img.crop((left, top, left + side, top + side))

        tensor = get_transform()(img).unsqueeze(0)

        with torch.no_grad():
            output = model(tensor)
            probs  = torch.softmax(output, dim=1)
            conf, predicted = torch.max(probs, 1)

        blood_group = class_names[predicted.item()]
        confidence  = round(conf.item(), 4)

        print(f"Natija: {blood_group}  ({confidence*100:.1f}%)\n")

        return jsonify({
            'blood_group': blood_group,
            'confidence':  confidence,
            'status':      'Muvaffaqiyatli'
        })

    except Exception as e:
        print(f"500 xato: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n🚀 MedAI ishga tushdi — http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)


