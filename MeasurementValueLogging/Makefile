qresource:
	pyrcc4 -o ui/qr.py ui/resource.qrc

translation-files:
	pylupdate4 -noobsolete ui.py ui/*.ui -ts ui/i18n/de.ts
	cd ui/i18n; lrelease de.ts
	make qresource

gh-pages:
	cd ../docs ; make gh-pages
