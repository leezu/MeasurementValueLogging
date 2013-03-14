qresource:
	pyrcc4 -o qr.py resource.qrc

translation-files:
	pylupdate4 ui.py ui/*.ui -ts i18n/de.ts
	cd i18n; lrelease de.ts
	make qresource

gh-pages:
	cd ../docs ; make gh-pages
