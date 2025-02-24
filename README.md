# 🔒 Sealed Secrets Generator

This is a **Flask-based web application** that allows users to **convert environment variables** into **Kubernetes Sealed Secrets**. It ensures sensitive data is safely encrypted using `kubeseal` before storing it in Kubernetes.

## 🚀 Features

✅ **Web Interface** – No need for CLI commands!  
✅ **Paste `.env` values** – Directly input environment variables in an IDE-like editor.  
✅ **Namespace Auto-detection** – Fetches available namespaces from the cluster.  
✅ **YAML Preview** – Shows a formatted preview of the generated sealed secret.  
✅ **Download Sealed Secret** – Save the generated secret as a `.yaml` file.  
✅ **Dependency Check** – Ensures `kubectl` and `kubeseal` are installed before running.  

---

## 📦 Installation

### 1️⃣ Install Dependencies
Ensure Python is installed, then run:
```sh
pip install -r requirements.txt
```

### 2️⃣ Install `kubectl` and `kubeseal`
Ensure these tools are installed **and in your system PATH**.

#### 🔹 **For Ubuntu/Debian**:
```sh
sudo apt install kubectl
curl -LO https://github.com/bitnami-labs/sealed-secrets/releases/latest/download/kubeseal-linux-amd64
sudo install -m 755 kubeseal-linux-amd64 /usr/local/bin/kubeseal
```

#### 🔹 **For macOS**:
```sh
brew install kubectl kubeseal
```

#### 🔹 **For Windows**:
```sh
choco install kubernetes-cli sealed-secrets
```

---

## 🛠 Usage

### 1️⃣ Start the Web App
Run:
```sh
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
Then, **open your browser** and go to:  
🔗 [http://localhost:8000](http://localhost:8000)

### 2️⃣ Convert `.env` to Sealed Secret
- **Paste** your environment variables.  
- **Select** the correct Kubernetes namespace.  
- **Click** "Generate Sealed Secret".  
- **Download** the `.yaml` file and apply it using:
  ```sh
  kubectl apply -f your-sealed-secret.yaml -n your-namespace
  ```


## 📜 License
This project is **open-source** and available under the MIT License.

---

## 💡 Contributing
Feel free to **open an issue** or submit a **pull request** for improvements! 🚀

