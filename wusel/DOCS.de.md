# Wusel

**von Wild & Weich · Version 0.7.0**

Beim Bearbeiten und Archivieren von Routinen wählen Eltern „Ab heute“ oder „Ab morgen“ (Standard). Neue Routinen gelten standardmäßig ab heute. Ab heute wird auch das aktuelle Tagesziel bewusst angepasst; ab morgen bleiben heutige Aufgaben und Tagesziel unverändert. Vorgemerkte Änderungen werden im Wochenplan angezeigt und ab dem gewählten Datum wirksam. Verdiente Abzeichen bleiben erhalten. Die Abzeichenansicht zeigt zuerst ein nächstes Ziel mit Fortschritt und verdiente Abzeichen; „Alle Abzeichen ansehen“ öffnet die Sammlung nach Schritten, ganzen Tagen und Serien.

17 Abzeichen belohnen Schritte (1, 5, 10, 20, 50, 100, 150, 250, 500, 1000), ganze Tage (1, 10, 30) und Serien (3, 7, 14, 30 aufeinanderfolgende Kalendertage). Ganze Tage zählen ab Version 0.6.0 und benötigen mindestens einen geplanten Schritt sowie alle Schritte erledigt. Tage ohne Schritte oder mit offenen Schritten unterbrechen die Serie; der laufende Tag hat bis Mitternacht Zeit. Frühere Tagespläne bleiben bei späteren Änderungen erhalten. Korrekturen aktualisieren die Serienwertung; verdiente Abzeichen bleiben erhalten und können von Eltern entzogen werden.

Eltern- und Kinderpasswörter benötigen mindestens 4 Zeichen. Datum und Uhrzeit folgen dem Gebietsschema des Browsers, mit ausgeschriebenen Monats- und Wochentagsnamen. Temperaturen werden als ganze Zahlen angezeigt.

Eine ruhige Routinen-App für Kinder und Eltern. Wusel läuft lokal auf Home Assistant OS auf einem Raspberry Pi 5 und wird über den Browser auf einem Tablet oder Smartphone bedient.

[English instructions](DOCS.md)

## Funktionen

- Ein nächster Schritt mit großer **Erledigt**-Taste, optionaler Anleitung und kleinem Tageszähler.
- Ein schmaler Stufenbalken, kurze Punkterückmeldungen und eine kleine Feier bei einer neuen Stufe. „Bewegung reduzieren“ wird berücksichtigt.
- Checkliste und Abzeichen auf Wunsch. Eltern wählen die Startansicht jedes Kindes.
- Eigene Eltern- und Kinderkonten. Alle Eltern dieser Installation verwalten alle Kinder.
- Routinen für Wochentage, Wochenenden, jeden Tag oder ein bestimmtes Datum.
- Deutsch und Englisch sowie fünf persönliche Farbwelten: Wald, Ozean, Beere, Lavendel und Sonnenschein.
- Eine kurze Wetterzeile mit ausführlicher Vorhersage auf Wunsch aus deiner Home Assistant Wetterintegration.

## Ordnerstruktur

Öffne nach dem Entpacken den äußeren Projektordner `wusel`:

```text
wusel/
  README.md
  README.de.md
  VALIDATION.md
  wusel/                 # Diesen inneren Ordner auf den Pi kopieren
    config.yaml
    Dockerfile
    app.py
    weather.py
    server.py
    requirements.txt
    static/
    translations/
    DOCS.md
    DOCS.de.md
  tests/
  tools/package.py
```

## Installation auf Home Assistant OS

1. Greife mit **Samba share** oder **Terminal & SSH** auf den Ordner für lokale Apps zu. Aktuelle Versionen stellen ihn unter `/local_apps` bereit, ältere Installationen gegebenenfalls unter `/addons`.
2. Kopiere den **inneren App-Ordner `wusel`** dorthin. Die Konfiguration liegt danach unter `/local_apps/wusel/config.yaml`, bei älteren Installationen unter `/addons/wusel/config.yaml`. Kopiere nicht den äußeren Projektordner mit Tests und Werkzeugen.
3. Öffne **Einstellungen → Apps → App installieren** und aktualisiere die Store-Liste. Ältere Versionen nennen den Bereich **Add-ons → Add-on-Store**. Installiere **Wusel** unter den lokalen Apps. Der erste Build benötigt Internet für Container und Python-Pakete.
4. Prüfe in Wusels Konfiguration `timezone`, zum Beispiel `Europe/Zurich`. Lass `secure_cookie` für lokalen HTTP-Zugriff auf `false`. Starte Wusel und aktiviere den automatischen Start.
5. Kopiere den **Einrichtungscode** aus Wusels Protokoll. Öffne die Weboberfläche und erstelle damit das erste Elternkonto. Es gibt keine vorgegebenen Zugangsdaten.
6. Lege unter **Familie** ein Kinderkonto an. Wähle das Kind und füge im **Wochenplan** Routinen hinzu.
7. Öffne auf dem Kindergerät `http://DEINE_HOME_ASSISTANT_IP:8099` und melde dich mit dem Kinderkonto an. Du kannst die Seite zum Startbildschirm hinzufügen. Das Kind benötigt kein Home Assistant Konto.

Die Ordner und den lokalen Installationsablauf erläutert Home Assistant in der [Einführung](https://contributors.home-assistant.io/apps/first-app/) und der [Testanleitung](https://contributors.home-assistant.io/apps/guides/testing/).

## Zugriff über IPv4 und IPv6

Ab Version 0.5.2 nutzt Wusel direkt das Netzwerk des Pi und lauscht über IPv4 und IPv6 auf dem festen HTTP-Port **8099**. Damit entfällt die bisherige reine IPv4-Portweiterleitung, wenn beispielsweise `homeassistant.local` auf eine IPv6-Adresse zeigt. Eine eigene Zuordnung für `8099/tcp` ist nicht mehr nötig; das entsprechende Netzwerkfeld kann daher entfallen. Port 8099 muss auf dem Pi frei sein.

Prüfe nach dem Update `http://homeassistant.local:8099/health` und die IPv4-Adresse des Pi, zum Beispiel `http://YOUR_PI_IP:8099/health`. Beide sollen `{"ok":true}` liefern. Im Protokoll erscheinen die Listener-Adressen (`0.0.0.0:8099` sowie `[::]:8099` bei aktiviertem IPv6) und anschließend `Wusel ready: HTTP port 8099`.

Übernimm alle neuen App-Dateien, einschließlich `server.py`, `Dockerfile` und `config.yaml`. Aktualisiere beziehungsweise baue die installierte App neu und prüfe Version **0.7.0**. Ein bloßer Neustart des alten Containers ändert den Netzwerkmodus noch nicht. Installationskennung und gespeicherte Daten bleiben erhalten.

Wusel teilt damit die Netzwerkschnittstellen des Pi. Dafür sind weder das Abschalten des Schutzmodus noch eine Portfreigabe am Router nötig. Die vorhandene Anmeldung und die Hinweise zu HTTP/HTTPS gelten weiterhin.

Technische Referenzen: [Waitress IPv4/IPv6-Listener](https://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html), [Home Assistant Host-Netzwerk](https://contributors.home-assistant.io/apps/reference/configuration/).

## Bestehende Installation aktualisieren

1. Erstelle ein Home Assistant Backup einschließlich Wusel und stoppe Wusel.
2. Suche Wusels bisherigen Quellordner im Ordner für lokale Apps. Benenne diesen bei Bedarf in `wusel` um und ersetze seine App-Dateien durch den Inhalt des neuen inneren Ordners `wusel`. Im überwachten App-Ordner soll nur eine Quellkopie dieser App liegen; sichere Quellkopien außerhalb davon.
3. Lass den Wert `slug` in `config.yaml` unverändert. Diese Kompatibilitätskennung bezeichnet die bestehende Installation und ist vom Anzeigenamen und Quellordner getrennt. Home Assistant identifiziert darüber die App und ihre gespeicherten Daten.
4. Aktualisiere die Store-Liste, führe das Update beziehungsweise einen Rebuild aus und starte Wusel. Behalte die App währenddessen installiert, damit ihr Datenvolume erhalten bleibt.

Konten, Routinen, Erledigungen, Sprachen und Farbwelten bleiben im dauerhaften Verzeichnis `/data` erhalten. Fehlende Einstellungen älterer Versionen werden automatisch ergänzt. Diese Version ergänzt IPv4/IPv6 im Host-Netzwerk und klare Startmeldungen; das Speicherformat bleibt gleich.

Die Trennung von Ordner und Installationskennung beschreibt Home Assistant unter [How apps work](https://contributors.home-assistant.io/apps/how-apps-work/).

## Bedienung im Alltag

**Kinder:** Erledige den nächsten Schritt über **Erledigt**. **Meinen Tag ansehen** öffnet die Checkliste mit Rückgängig-Funktion. **Meine Abzeichen** öffnet die Belohnungen. Unter **Einstellungen** stehen Sprache, Farbwelt und Abmelden bereit. Antippen der Wetterzeile öffnet die Vorhersage.

**Eltern:** Unter **Familie** lassen sich Konten anlegen, Passwörter zurücksetzen und Startansichten wählen. Im **Wochenplan** werden Routinen erstellt oder bearbeitet. Unter **Prüfen** können Erledigungen zurückgenommen oder wiederhergestellt werden. **Abzeichen** erlaubt das Entfernen und Wiederherstellen von Abzeichen. Eltern wählen ihre Farben unter **Einstellungen**; Sprache und Abmelden stehen im Kontomenü oben rechts. Kinderseiten sind unter dem ausgewählten Kind zusammengefasst; Familie und Einstellungen stehen separat unter Verwaltung.

Ein erledigter Schritt gibt zehn Punkte. Alle hundert Punkte folgt eine neue Stufe. Abzeichen gibt es nach 1, 5, 20, 50 und 100 erledigten Schritten. Wiederholtes Tippen und Rückgängig/Wiederankreuzen erzeugen keine zusätzlichen Punkte und spielen die Punkteanimation nicht erneut ab. Eine Elternkorrektur entfernt die Punkte und sperrt die Erledigung bis zur Wiederherstellung. Entferne ein zu Unrecht erhaltenes Abzeichen separat.

Für andere Uhrzeiten am Wochenende legst du zwei Routinen mit unterschiedlichen Tagen an. Eine Datumsaufgabe kommt an diesem Datum hinzu; sie setzt bestehende Routinen nicht aus. Uhrzeiten dienen zur Orientierung und lösen keinen Alarm aus.

Sprache und Farbwelt werden pro Konto geräteübergreifend gespeichert. Routinentitel und Anleitungen bleiben so, wie sie eingegeben wurden. Melde dich auf gemeinsam genutzten Geräten vor dem Kontowechsel ab.

## Wetter einrichten

Trage in Wusels Home Assistant Konfiguration bei `weather_entity` die ID einer Wetterentität für deinen Ort ein, etwa `weather.forecast_home`, und starte Wusel neu. Ein leerer Wert deaktiviert das Wetter. Entitäts-IDs findest du unter **Einstellungen → Geräte & Dienste → Entitäten**.

```yaml
timezone: Europe/Zurich
weather_entity: weather.forecast_home
secure_cookie: false
```

Stündliche Vorhersagen hängen vom gewählten Anbieter ab. Eine reine Tagesvorhersage wird gekennzeichnet; fehlende Werte werden nicht erfunden. Temperaturen verwenden die Einheit aus Home Assistant, Zeiten die eingestellte Zeitzone. Wetterausfälle verhindern keine Häkchen. Veraltete Daten werden gekennzeichnet und Kleidungshinweise dann ausgeblendet.

Wusel nutzt serverseitig das Supervisor-Token und die Berechtigung `homeassistant_api` für Wetterzustand und Vorhersagen. Das Token gelangt nicht in den Browser. Vorschaubilder enthalten gekennzeichnetes Beispielwetter.

## Daten und derzeitige Grenzen

Nimm Wusel in deine Home Assistant Backups auf. Die App fordert kalte Backups an, bei denen SQLite für die Kopie gestoppt wird. Backups enthalten Familiendaten und sollten privat bleiben.

Diese Version ist für das vertrauenswürdige Heimnetz gedacht. Zugriff von unterwegs erfordert einen passend eingerichteten HTTPS-Zugang oder ein privates VPN. Aktiviere `secure_cookie` nur bei HTTPS. Ingress, Push-Nachrichten, Offlinebetrieb, Passwortwiederherstellung per E-Mail sowie das Löschen oder Deaktivieren von Konten sind noch nicht enthalten. Auch Kontoumbenennung, Rollenwechsel und die Zuordnung einzelner Kinder zu bestimmten Eltern sind noch nicht umgesetzt.

## Lokal starten

Benötigt Python 3.12 oder neuer. Im äußeren Projektordner, mit PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\wusel\requirements.txt
$env:GARDEN_DATA = Join-Path $PWD "work\dev-data"
$env:GARDEN_DEV = "1"
.\.venv\Scripts\python.exe .\wusel\app.py
```

Öffne `http://127.0.0.1:8099` und verwende den Einrichtungscode aus dem Terminal. Die vorhandenen Umgebungsvariablen `GARDEN_*` bleiben aus Kompatibilitätsgründen erhalten. Der Entwicklungsserver bindet nur an localhost; der Container verwendet Waitress.

## Prüfen und Paket erstellen

Im äußeren Projektordner:

```powershell
python -m unittest discover -s tests -v
node tests/test_i18n.cjs
python tools/package.py
```

Das Paketwerkzeug schreibt `wusel-0.7.0.zip` in den Unterordner `dist` des Projekts. Im ZIP liegt die App-Konfiguration unter `wusel/wusel/config.yaml`. Lokale Daten, virtuelle Umgebungen und Bytecode werden nicht eingepackt.

Prüfungen und Grenzen stehen in [VALIDATION.md](../VALIDATION.md). Der Produktionsserver wurde lokal über IPv4 und IPv6 geprüft. Der neue Container-Netzwerkmodus, der Zugriff über den Hostnamen, Live-Wetter und Backup/Wiederherstellung müssen nach dem Update auf dem Pi überprüft werden.
