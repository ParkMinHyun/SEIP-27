all:
	pdflatex paper.tex > /dev/null
	bibtex paper > /dev/null
	pdflatex paper.tex > /dev/null
	pdflatex paper.tex > /dev/null

clean:
	rm *.blg *.bbl *.aux *.log *.dvi *.out *.pdf
