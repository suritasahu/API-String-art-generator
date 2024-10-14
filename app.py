from flask import Flask, request, send_file
import os
import matplotlib.pyplot as plt
from stringart import StringArtGenerator

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/generate', methods=['POST'])
def generate_string_art():
    if 'image' not in request.files:
        return {"error": "No image file provided"}, 400

    file = request.files['image']
    if file.filename == '':
        return {"error": "No selected file"}, 400

    # Save the uploaded image
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    # Create a StringArtGenerator instance and process the image
    generator = StringArtGenerator()
    generator.load_image(image_path)
    generator.preprocess()
    generator.set_nails(180)
    generator.set_seed(42)
    generator.set_iterations(4000)
    
    # Generate the pattern
    pattern = generator.generate()

    # Prepare the output image file path
    result_image_path = os.path.join(RESULT_FOLDER, 'result.png')

    # Plotting and saving the result
    lines_x = []
    lines_y = []
    for i, j in zip(pattern, pattern[1:]):
        lines_x.append((i[0], j[0]))
        lines_y.append((i[1], j[1]))

    plt.figure(figsize=(8, 8))
    plt.axis('off')
    plt.plot(lines_x, lines_y, linewidth=0.1, color='k')
    plt.savefig(result_image_path, bbox_inches='tight', pad_inches=0)

    return send_file(result_image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
