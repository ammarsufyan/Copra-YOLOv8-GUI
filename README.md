# Copra-YOLOV8-GUI

Copra Detection GUI using YOLOv8 model with custom dataset, GUI using Tkinter and OpenCV. This GUI integrates industrial machine using PySerial with 2 COMs for Embedded Microcontroller (ESP32/STM32).

## Step-by-step to Run the Apps

1. Install Python [3.10.11](https://www.python.org/downloads/release/python-31011/).

2. Install the requirements.
    ```
    pip install -r requirements.txt
    ```

3. Next, if using RTX GPU, install the [Pytorch with CUDA](https://pytorch.org/get-started/locally/).
    ```
    pip uninstall torch torchaudio torchvision
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    ```

4. Run the apps
    ```
    cd apps
    python app_copra_v8_no_infrared_two_lines.py
    ```

## Citations and Acknowledgements

Glenn Jocher, Ayush Chaurasia, Alex Stoken, Jirka Borovec, NanoCode012, Yonghye Kwon, Kalen Michael, TaoXie, Jiacong Fang, imyhxy, Lorna, 曾逸夫(Zeng Yifu), Colin Wong, Abhiram V, Diego Montes, Zhiqiang Wang, Cristi Fati, Jebastin Nadar, Laughing, … Mrinal Jain. (2022). ultralytics/yolov5: v7.0 - YOLOv5 SOTA Realtime Instance Segmentation (v7.0). Zenodo. https://doi.org/10.5281/zenodo.7347926.