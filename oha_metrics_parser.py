"""
    Download a PDF from OHA
    Parse it
    Update a local database and generate a static web page
"""
import camelot
import pandas as pd

if __name__ == "__main__":

    frames = []
    for page in ["1","2","3"]:
        t = camelot.read_pdf("Weekly-County-Metrics.pdf", pages=page)
        df = t[0].df
        # Make first row into header
        df.columns = df.iloc[0]
        df = df.drop(df.index[0]) # get rid of row in table
        print(t[0].parsing_report)
        frames.append(df)
        print(df)
        pass
    df = pd.concat(frames)


    print(df)

    rural = [
        "Clatsop",
        "Columbia",
        "Tillamook"
    ]
    metro = [
        "Multnomah",
        "Clackamas",
        "Washington"
    ]

    # Gather information on these interesting rows.
    interesting = [
        "Oregon",
    ] + rural + metro

    for i in df.iterrows():
        # Column 0 will be a name and some date stamps
        # The first token will be a place (state or county)
        # the remaining tokens will be dates; ignore non date strings.
        col0 = i[1][0].split('\n')
        place = col0[0].replace(',','')
        if not place in interesting: continue

        dates = []
        for token in col0[1:]:
            try:
                dates.append(token.strptime("%M/%D/%Y"))
            except:
                pass
        print(place, dates)

        # Column 1 will be 3 pairs of numbers, "case rate/100k" and "positive rate"
        col1 = i[1][1].split('\n')

        print(col0)
        print(col1)
        print()
