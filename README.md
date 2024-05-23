### 1. Clone the repository:
   ```shell
   git clone https://github.com/vladysllav/crypto-projects.git
   ```

### 2. Create a `.env` file based on the `.env.example` file:
   ```shell
   cd crypto-projects/account_manager
   ```
   ```shell
   cp .env.example .env
   ```

### 3. To run, execute:
   ```shell
   docker build -t account_manager:latest .
   ```
   ```shell
   docker compose up -d
   ```