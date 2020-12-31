# corona_collector/app

This is a Dash/Plotly app for visualizing corona_collector data.

## Set up

I have to pin the Python version because sundry dependencies
won't work with 3.8+ due to Windows DLL problems. Might work with 3.9
on Linux... don't know...

Currently I am maintaining a separate environment for Dash, I did not see a reason
to pack the covid environment full of dependencies it does not need.

There are some packages in there that are probably just baggage from a
tutorial, like [Seaborn(https://seaborn.pydata.org/)] for instance.

```bash
conda create --name=dash python=3.6.12
conda install --name=dash --file=requirements.txt
conda activate dash
```

## Debugging

There is a Visual Studio Code launch.json option for Dash.
It will open a Chrome debug window.

## Deployment

I will write this the first time I actually deploy.
It will be in a Docker container running waitress,
based on the one I use for webforms.

