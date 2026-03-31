from flask import Flask, render_template, jsonify, request
import numpy as np
from scipy.spatial.transform import Rotation
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert_rotation():
    data = request.json
    input_format = data['format']
    values = np.array(data['values'], dtype=float)
    input_degrees = data.get('inputDegrees', True)
    output_degrees = data.get('outputDegrees', True)
    input_rotation_order = data.get('inputRotationOrder', 'xyz')
    output_rotation_order = data.get('outputRotationOrder', 'xyz')
    # Always intrinsic (uppercase = body-fixed axes, standard in robotics/URDF/ROS)
    in_order  = input_rotation_order.upper()
    out_order = output_rotation_order.upper()
    D = 8  # decimal places

    def r8(v):
        return round(float(v), D)

    try:
        if input_format == 'euler':
            r = Rotation.from_euler(in_order, values, degrees=input_degrees)
        elif input_format == 'quaternion':
            # UI provides [w, x, y, z]; scipy expects [x, y, z, w]
            r = Rotation.from_quat([values[1], values[2], values[3], values[0]])
        elif input_format == 'matrix':
            r = Rotation.from_matrix(values.reshape(3, 3))
        elif input_format == 'axis-angle':
            angle = values[0]
            axis = values[1:]
            norm = np.linalg.norm(axis)
            axis = np.array([0.0, 0.0, 1.0]) if norm < 1e-10 else axis / norm
            if input_degrees:
                angle = np.deg2rad(angle)
            r = Rotation.from_rotvec(angle * axis)
        elif input_format == 'rotvec':
            # UI provides [x, y, z] rotation vector (Rodrigues)
            # magnitude = angle; direction = axis
            if input_degrees:
                angle = np.linalg.norm(values)
                axis  = np.array([0.0, 0.0, 1.0]) if angle < 1e-10 else values / angle
                values = axis * np.deg2rad(angle)
            r = Rotation.from_rotvec(values)
        else:
            return jsonify({'error': 'Invalid format'}), 400

        euler = r.as_euler(out_order, degrees=output_degrees)
        quat = np.roll(r.as_quat(), 1)  # scipy [x,y,z,w] → [w,x,y,z]
        matrix = r.as_matrix()
        rotvec = r.as_rotvec()

        angle_out = np.linalg.norm(rotvec)
        axis_out = np.array([0.0, 0.0, 1.0]) if angle_out < 1e-10 else rotvec / angle_out
        if output_degrees:
            angle_out = np.rad2deg(angle_out)

        return jsonify({
            'euler': [r8(v) for v in euler],
            'quaternion': [r8(v) for v in quat],
            'matrix': [[r8(v) for v in row] for row in matrix],
            'axisAngle': {
                'angle': r8(angle_out),
                'axis': [r8(v) for v in axis_out]
            },
            'rotvec': [r8(v) for v in rotvec],
            'units': 'degrees' if output_degrees else 'radians',
            'outputRotationOrder': output_rotation_order,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
