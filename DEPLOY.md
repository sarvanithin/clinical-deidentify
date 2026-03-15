# 🌍 Deploying to a Public URL

To share your Clinical De-identification Dashboard with others, follow these steps to deploy it to **Hugging Face Spaces**.

## Prerequisites
1. A [Hugging Face](https://huggingface.co/join) account.
2. Your project already pushed to your [GitHub Repository](https://github.com/sarvanithin/clinical-deidentify).

## Step-by-Step Deployment

### 1. Create a New Space
- Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
- **Space Name**: Give it a name (e.g., `clinical-deidentify`).
- **SDK**: Select **Docker**.
- **Docker Template**: Choose **Blank**.
- **Pricing**: The **Free (16GB RAM)** tier is perfect for this models.

### 2. Connect to GitHub
- Instead of uploading files manually, click on the **"Settings"** tab of your new Space.
- Scroll down to **"GitHub Repo"**.
- Click **"Connect"** and select your `clinical-deidentify` repository.
- Ensure the branch is set to `main`.

### 3. Automatic Deployment
- Once connected, Hugging Face will detect your `Dockerfile`.
- It will automatically start building the image and downloading the transformer model.
- After a few minutes, your dashboard will be live at `https://huggingface.co/spaces/YOUR_USER/clinical-deidentify`!

## Why Hugging Face Spaces?
- **High RAM**: Clinical-NER models require several GBs of RAM; HF Spaces provides 16GB for free.
- **CI/CD**: Every time you `git push` to GitHub, your public URL will automatically update.
- **Privacy**: You can set the Space to **Private** if you only want specific people to access it.

---
*Note: Ensure you have performed the final `git push` from your local machine before connecting to GitHub.*
