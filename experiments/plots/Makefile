SHELL=/bin/bash
.PHONY: rho

optimize_rfc:
	python plot.py rfc 100
	cd figure/rfc; pdflatex mvrisk_optimized_comparison.tex
	cd figure/rfc; pdflatex bounds_optimized_comparison.tex
	cd figure/rfc; rm -f *_optimized_comparison.{log,aux}; rm -f texput.log
	cp ../out/optimize/rfc/rho-{Phishing,Letter}.csv figure/rfc/datasets/
	cd figure/rfc; pdflatex plot_rhos.tex; rm -f plot_rhos.{log,aux}
	cd table/rfc; pdflatex optimize_test_risk.tex
	cd table/rfc; pdflatex optimize_bound.tex
	cd table/rfc; pdflatex optimize_values.tex
	cd table/rfc; rm -f optimize_*.{log,aux}
	rm -f texput.log

optimize_mce:
	python plot.py mce 7
	cd figure/mce; pdflatex mvrisk_optimized_comparison.tex
	cd figure/mce; pdflatex bounds_optimized_comparison.tex
	cd figure/mce; rm -f *_optimized_comparison.{log,aux}; rm -f texput.log
	cp ../out/optimize/mce/rho-{Phishing,Connect-4}.csv figure/mce/datasets/
	cd figure/mce; pdflatex plot_rhos.tex; rm -f plot_rhos.{log,aux}
	cd table/mce; pdflatex optimize_test_risk.tex
	cd table/mce; pdflatex optimize_bound.tex
	cd table/mce; pdflatex optimize_values.tex
	cd table/mce; rm -f optimize_*.{log,aux}
	rm -f texput.log

clean:
	cd figure/mce; rm -f *.pdf; rm -rf datasets
	cd figure/rfc; rm -f *.pdf; rm -rf datasets
	cd table/mce; rm -f *.pdf; rm -rf optimize
	cd table/rfc; rm -f *.pdf; rm -rf optimize
