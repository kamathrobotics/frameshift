# 3D Rotation Converter

A simple web application to convert between different 3D rotation formats (Euler angles, quaternions, rotation matrices, and axis-angle representations) with real-time 3D visualization.

## Features

- Convert between:
  - Euler angles (XYZ)
  - Quaternions
  - Rotation matrices
  - Axis-angle representation
- Real-time 3D visualization using Three.js
- Interactive 3D viewer with orbit controls

## Local Development

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Select the input rotation format from the dropdown
2. Enter the rotation values in the corresponding input fields
3. Click "Convert" to see the rotation represented in all formats
4. The 3D viewer will update to show the rotation
5. Use your mouse to orbit around the 3D view:
   - Left click + drag to rotate the view
   - Right click + drag to pan
   - Scroll to zoom

## Technologies Used

- Backend:
  - Python
  - Flask
  - NumPy
  - SciPy
- Frontend:
  - Three.js for 3D visualization
  - Vanilla JavaScript
  - HTML/CSS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this code for any purpose.
