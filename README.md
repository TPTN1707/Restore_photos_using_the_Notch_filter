# Restore Photos Using Notch Filter

## 📌 Overview
This project focuses on **restoring degraded images** by removing periodic noise using **Notch Filters** in the frequency domain.  
The application provides an **interactive GUI** that allows users to manually select noise frequencies and apply different types of Notch filters.

The project is implemented in **Python**, combining **Fourier Transform techniques** with a user-friendly **Tkinter-based interface**.

---

## 🎯 Objectives
- Remove periodic noise from images in the frequency domain
- Apply and compare different Notch filtering techniques
- Provide an interactive tool for educational and experimental purposes

---

## 🧠 Implemented Notch Filters

### 1. Ideal Notch Filter
- Completely removes selected frequency components
- Sharp cutoff in the frequency domain
- May introduce ringing artifacts

### 2. Butterworth Notch Filter
- Smooth frequency response
- Controlled by filter order
- Trade-off between sharpness and smoothness

### 3. Gaussian Notch Filter
- Smoothest frequency response
- Minimizes ringing effects
- Best visual quality in most cases

---

## 🖥️ Application Features
- Load and preview grayscale images  
- Compute and display **DFT spectrum**  
- Manually select noise frequencies using mouse clicks  
- Choose Notch filter type and parameters:
  - Number of notch points
  - Bandwidth radius
  - Butterworth filter order
- View filtered image in real-time
- Display comparison summary:
  - Original image
  - Filtered image
  - DFT before filtering
  - DFT after filtering
- Save the restored image

---


## ⚙️ Installation & Requirements

### Required Libraries
```bash
pip install numpy opencv-python pillow matplotlib ttkbootstrap
```

---
## 📊 Frequency Domain Processing

The image restoration process follows these steps:

1. Convert image to grayscale

2. Apply 2D Fast Fourier Transform (FFT)

3. Shift the spectrum to center frequencies

4. Apply selected Notch filter

5. Perform inverse FFT

6. Display and save restored image
---