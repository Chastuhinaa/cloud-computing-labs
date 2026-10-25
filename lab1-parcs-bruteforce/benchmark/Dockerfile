FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir matplotlib
COPY bruteforce_mp.py plot_results.py ./
CMD ["sh", "-c", "python bruteforce_mp.py --maxlen 4 --stretch 2 --password help --workers 1 2 3 4 --out results.csv && python plot_results.py results.csv results.png"]
