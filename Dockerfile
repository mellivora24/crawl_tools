# Cài system deps cho Chromium & Qt6
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libglib2.0-0 libnss3 libdbus-1-3 libxkbcommon0 libx11-xcb1 \
    libxcomposite1 libxcursor1 libxi6 libxtst6 libatk1.0-0 \
    libatk-bridge2.0-0 libgtk-3-0 libdrm2 libgbm1 libxrandr2 \
    libasound2 fonts-liberation fonts-unifont fonts-ubuntu \
    curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# Cài Chromium cho Playwright (không dùng --with-deps nữa)
RUN python -m playwright install chromium
