# open-ai

Repositorio con diversos proyectos y ejemplos relacionados con **Open-Source AI Stack**.


## 📌 Uso
Cada directorio contiene documentación y código relevante para distintos casos de uso en **Open-Source AI Stack**.

### 1. Set up Docker's apt repository.

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

### 2. Install the Docker packages.

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 3. Verify that the installation is successful by running the hello-world image:

```bash
sudo docker run hello-world
```

This command downloads a test image and runs it in a container. When the container runs, it prints a confirmation message and exits.

Ref: https://docs.docker.com/engine/install/ubuntu/

### 4. To install Git, run the following command:

```bash
sudo apt-get install git-all
```

### 5. Once the command output has been completed, you can verify the installation by typing:

```bash
sudo git version
```

Ref: https://github.com/git-guides/install-git

### 6. ....:

```bash
sudo mkdir docker
cd docker
sudo git clone https://github.com/jganggini/open-ai.git
cd docker-open-webui-auto-https
```

### 7. ....:

For Nvidia GPU setups:

```bash
sudo docker compose --profile gpu-nvidia pull
sudo docker compose create
sudo docker compose --profile gpu-nvidia up
```

For Non-GPU setups:

```bash
sudo docker compose --profile cpu pull
sudo docker compose create
sudo docker compose --profile cpu up
```

### 8. ....:



Ref: https://github.com/n8n-io/self-hosted-ai-starter-kit