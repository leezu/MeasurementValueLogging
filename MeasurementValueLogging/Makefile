qresource:
	pyrcc4 -o qr.py resource.qrc

translation-files:
	pylupdate4 ui.py ui/*.ui -ts i18n/de.ts
	cd i18n; lrelease de.ts

gh-pages:
	cd ../docs ; make gh-pages