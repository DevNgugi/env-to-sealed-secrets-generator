import os
import subprocess
import yaml
import re
from flask import Flask, request, render_template, send_file
from kubernetes import client, config
import shutil
from kubernetes.client.exceptions import ApiException

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_kubernetes_connection():
    try:
        # Load Kubernetes configuration
        config.load_kube_config()  # Use load_incluster_config() if running inside a cluster
        v1 = client.CoreV1Api()
        v1.list_namespace()  # Try fetching namespaces
        return True
    except (ApiException, Exception):
        return False  # Return False if connection fails
        
# Load Kubernetes config and fetch available namespaces
def get_kubernetes_namespaces():
    try:
        config.load_kube_config()  # Use kubeconfig if running locally
        v1 = client.CoreV1Api()
        namespaces = [ns.metadata.name for ns in v1.list_namespace().items]
        return namespaces
    except Exception:
        return ["default"]  # Fallback if unable to connect to cluster
def check_dependencies():
    """Check if kubectl and kubeseal are in the system PATH."""
    missing_tools = []
    
    if not shutil.which("kubectl"):
        missing_tools.append("kubectl")
    
    if not shutil.which("kubeseal"):
        missing_tools.append("kubeseal")

    return missing_tools

# Validate .env content
def validate_env(env_content):
    lines = env_content.strip().split("\n")
    env_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=.*$")  # Format: KEY=VALUE
    seen_keys = set()

    for line in lines:
        if not line or line.startswith("#"):  # Allow comments and empty lines
            continue
        if not env_pattern.match(line):
            return f"❌ Invalid format: {line}"
        key = line.split("=")[0]
        if key in seen_keys:
            return f"❌ Duplicate key: {key}"
        seen_keys.add(key)

    return None  # No errors

@app.route("/", methods=["GET", "POST"])
def index():
    missing_tools = check_dependencies()
    
    if missing_tools:
        error_message = (
            f"❌ The following tools are missing: {', '.join(missing_tools)}.<br>"
            "Please install them and ensure they are in your system PATH.<br><br>"
            "<strong>Installation Guide:</strong><br>"
            "<code>sudo apt install kubectl</code> (Ubuntu/Debian)<br>"
            "<code>brew install kubectl</code> (MacOS)<br>"
            "<code>choco install kubectl</code> (Windows)<br><br>"
            "<code>curl -LO https://github.com/bitnami-labs/sealed-secrets/releases/latest/download/kubeseal-linux-amd64</code><br>"
            "<code>sudo install -m 755 kubeseal-linux-amd64 /usr/local/bin/kubeseal</code>"
        )
        return render_template("error.html", error_message=error_message)
    if not check_kubernetes_connection():
        return render_template("error.html", error_message="❌ Unable to connect to Kubernetes. Please check your configuration.")  

    namespaces = get_kubernetes_namespaces()

    if request.method == "POST":
        env_content = request.form.get("env_content", "").strip()
        namespace = request.form.get("namespace", "default")
        secret_name=request.form.get("secret_name")

        if not env_content:
            return "❌ Error: No input provided", 400
        if not secret_name:
            return "❌ Error: Secret Name Provided", 400

        # Validate env input
        validation_error = validate_env(env_content)
        if validation_error:
            return render_template("index.html", namespaces=namespaces, error_message=validation_error)

        # Save env content to a temp file
        env_file_name = secret_name
        env_file_path = os.path.join(UPLOAD_FOLDER, env_file_name)
        with open(env_file_path, "w") as f:
            f.write(env_content)

        secret_name = f"{env_file_name}-secret"
        secret_yaml_path = os.path.join(UPLOAD_FOLDER, f"{secret_name}.yaml")
        sealed_yaml_path = os.path.join(UPLOAD_FOLDER, f"{secret_name}-sealed.yaml")

        try:
            # Create Kubernetes Secret
            subprocess.run(
                [
                    "kubectl", "create", "secret", "generic", secret_name,
                    f"--from-file={env_file_path}",
                    "--dry-run=client", "-o", "yaml",
                    "-n", namespace  # Add namespace flag
                ],
                check=True,
                stdout=open(secret_yaml_path, "w"),
            )

            # Seal the Secret
            with open(secret_yaml_path, "rb") as secret_yaml:
                subprocess.run(
                    ["kubeseal", "--format", "yaml"],
                    stdin=secret_yaml,
                    stdout=open(sealed_yaml_path, "w"),
                    check=True,
                )

            # Load and format the sealed secret
            with open(sealed_yaml_path, "r") as sealed_yaml_file:
                sealed_secret_yaml = yaml.safe_load(sealed_yaml_file)

            sealed_yaml_filename = os.path.basename(sealed_yaml_path)
            print(sealed_yaml_filename,'*******************')

            return render_template(
                    "sealed_secret.html",
                    sealed_secret=sealed_secret_yaml,
                    download_file=sealed_yaml_filename  # Pass only the filename
                )

        except subprocess.CalledProcessError as e:
            return f"❌ Error: {str(e)}", 500

    return render_template("index.html", namespaces=namespaces, error_message="")

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
