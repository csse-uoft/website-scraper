
#### Install Dependencies
```shell
conda env create -f PyWebScraper.yml
```
#### Run
```shell
conda activate PyWebScraper
python main.py -u http://domain.com
```

##### Paramters
- `-u` : Starting URL to parse (e.g. http://main.com).
- `-m` : XPath to look for main content (e.g. 'div.main', 'div[id=\"main\"]').
- `-n` : XPath to look for site navigation links (e.g. 'div.nav a').
- `-js` : Whether to run JavaScript on page or not (0=False, 1=True (default)).