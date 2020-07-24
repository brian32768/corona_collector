import os
import sys
from app import app

# This is how we launch in docker.
# In VSCODE we launch from launch.json

if __name__ == "__main__":
    for k in os.environ:
        print(k, os.environ[k])

    port = 5001
    try:
        port = sys.argv[1]
    except:
        pass
    print("Starting cases service on port", port)
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')

# That's all!
