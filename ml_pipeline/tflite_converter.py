import tensorflow as tf
import numpy as np
import os

def convert_to_tflite_c_array(model, representative_dataset_X=None):
    """
    Converts a Keras model to a quantized TensorFlow Lite model and exports
    it as a C byte array for inclusion in ESP32 firmware.
    """
    print("\nConverting model to TFLite (Quantized)...")
    
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Enable optimizations
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # If we have representative dataset, enforce full integer quantization for microcontrollers
    if representative_dataset_X is not None:
        def representative_data_gen():
            for i in range(100):
                # Ensure correct shape and type
                data = representative_dataset_X[i:i+1].astype(np.float32)
                yield [data]
        
        converter.representative_dataset = representative_data_gen
        
        # Ensure that if any ops can't be quantized, the converter throws an error
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        
        # Set input/output types to int8 (or float32 depending on user preference, int8 is faster)
        # We will keep default float32 interfaces for simplicity, but internal weights are int8.
        converter.inference_input_type = tf.float32 
        converter.inference_output_type = tf.float32

    tflite_model = converter.convert()
    
    tflite_model_path = 'data/asthma_model.tflite'
    with open(tflite_model_path, 'wb') as f:
        f.write(tflite_model)
        
    print(f"Saved TFLite model to {tflite_model_path}")
    print(f"TFLite model size: {len(tflite_model)} bytes")
    
    # Convert to C array
    hex_array = []
    for i, b in enumerate(tflite_model):
        hex_array.append(f'0x{b:02x}')
    
    hex_array_str = ', '.join(hex_array)
    
    c_file_content = f"""// Automatically generated TFLite model array
// Model size: {len(tflite_model)} bytes

#include "model_data.h"

// Align the memory to 16 bytes for optimal performance on 32-bit MCUs
alignas(16) const unsigned char g_model[] = {{
    {hex_array_str}
}};

const int g_model_len = {len(tflite_model)};
"""
    
    c_file_path = '../firmware/model_data.cpp'
    h_file_path = '../firmware/model_data.h'
    
    # Create the H file
    h_file_content = """#ifndef MODEL_DATA_H
#define MODEL_DATA_H

extern const unsigned char g_model[];
extern const int g_model_len;

#endif // MODEL_DATA_H
"""
    os.makedirs('../firmware', exist_ok=True)
    
    with open(c_file_path, 'w') as f:
        f.write(c_file_content)
        
    with open(h_file_path, 'w') as f:
        f.write(h_file_content)
        
    print(f"Exported C Array to {c_file_path} and {h_file_path}")
