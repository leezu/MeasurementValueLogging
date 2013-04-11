qresource:
	pyrcc4 -o ui_data/qr.py ui_data/resource.qrc

translation-files:
	pylupdate4 -noobsolete ui.py ui_data/*.ui -ts ui_data/i18n/de.ts
	cd ui_data/i18n; lrelease de.ts
	make qresource

gh-pages:
	cd ../docs ; make gh-pages
