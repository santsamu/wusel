# Wusel

**von Wild & Weich · Version 0.12.2**

Ab Version 0.12.0 lautet die Installationskennung `wusel` (lokal: `local_wusel`). Diese Version ist eine saubere Neuinstallation mit neuer Datenbank `/data/wusel.sqlite3`, `WUSEL_*`-Umgebungsvariablen und neuen Sitzungskennungen. Frühere Installationskennungen und Daten werden nicht übernommen. Kopiere die aktuelle innere App-Struktur nach `/local_apps/wusel` (beziehungsweise `/addons/wusel`), lade den Store neu und installiere Wusel neu. Richte danach das erste Elternkonto mit dem Einrichtungscode aus den Logs ein.

Eltern erhalten im Aufgabenformular Hinweise für kurze, konkrete Schritte und können eine optionale erste kleine Handlung ergänzen. Die Kinderansicht zeigt diese direkt unter dem Titel. „Ich brauche Hilfe“ öffnet die vorhandene Anleitung; „Erwachsenen fragen“ fordert dazu auf, einen Erwachsenen vor Ort zu holen. Es wird keine Nachricht versendet. „Später wiederkommen“ verschiebt den Schritt hinter andere offene Schritte desselben Tages, ohne ihn abzuhaken oder Punkte zu verändern. Gibt es keinen anderen verfügbaren Schritt, bleibt diese Option mit Erklärung deaktiviert. Unter Familie → Unterstützung für Kinder können Eltern pro Kind Serien-Abzeichen ausblenden und ruhige Belohnungen aktivieren. Verdiente Abzeichen und Punkte bleiben erhalten; ruhige Belohnungen unterdrücken Punkteanimationen, Level-Jubel und Abzeichenmeldungen unabhängig von der Geräteeinstellung. Korrekturen verwenden neutrale Formulierungen; Eltern behalten ihre bisherigen Kontrollen. Die neuen Einstellungen bleiben beim Upgrade standardmäßig auf Serien sichtbar/ruhige Belohnungen aus. Beim Zurücksetzen werden sie und die Zurückstellungen gelöscht, Aufgaben samt Anleitung bleiben erhalten.

Aufgaben können ein optionales Symbol erhalten, etwa Zahnbürste, Kleidung, Essen, Schulranzen, Bett oder Medikament. Eltern wählen das Symbol beim Erstellen oder Bearbeiten einer Aufgabe; „Kein Symbol“ ist der Standard. Das Symbol erscheint zusätzlich zum Aufgabentext in Fokusansicht, Tagesliste und Wochenplan. Die bestehende Auswahl „Ab heute/ab morgen“ gilt auch für Symboländerungen. Das Medikamentensymbol ist eine visuelle Merkhilfe und bestätigt keine tatsächliche Einnahme.

Die Kinderansicht unterscheidet „Jetzt dran“ und „Später heute“, ohne Schritte zu sperren. Nach dem Erledigen ist 15 Sekunden lang direktes Rückgängigmachen möglich; bei Tastaturfokus bleibt die Aktion länger verfügbar. Speicher- und Verbindungsstatus sind sichtbar. Bei unklarer Speicherung wird nur der Stand abgefragt, nicht automatisch erneut gespeichert. Das nächste Abzeichenziel bleibt bis zum Erreichen stabil; vollständige Verleihungsdaten sind aufklappbar und lesbar. Eltern-Rückmeldungen nennen Kind und Gültigkeitszeitpunkt. Unter Wochenplan → Pausentage verwalten lassen sich heute und zukünftige Zeiträume planen oder entfernen. Pausentage erhöhen und unterbrechen eine Serie nicht; Aufgaben sind freiwillig, ihre Erledigung gibt weiterhin Punkte. Vergangene Pausentage bleiben unverändert.

Eltern können unter Familie den Fortschritt eines Kinderkontos endgültig zurücksetzen. Gelöscht werden Erledigungen, Punkte, Abzeichen, Tages- und Serienfortschritt, geplante Pausentage sowie persönliche Einstellungen. Das Kind startet wieder auf Level 1 und wird auf allen Geräten abgemeldet. Name, Benutzername, Passwort und alle erstellten Aufgaben (auch archivierte Aufgaben und vorgemerkte Änderungen) bleiben erhalten. Bestätigung: Benutzername des Kindes und aktuelles Elternpasswort. Der Vorgang wird im Elternprotokoll dokumentiert.

Beim Bearbeiten und Archivieren von Routinen wählen Eltern „Ab heute“ oder „Ab morgen“ (Standard). Neue Routinen gelten standardmäßig ab heute. Ab heute wird auch das aktuelle Tagesziel bewusst angepasst; ab morgen bleiben heutige Aufgaben und Tagesziel unverändert. Vorgemerkte Änderungen werden im Wochenplan angezeigt und ab dem gewählten Datum wirksam. Verdiente Abzeichen bleiben erhalten. Die Abzeichenansicht zeigt zuerst ein nächstes Ziel mit Fortschritt und verdiente Abzeichen; „Alle Abzeichen ansehen“ öffnet die Sammlung nach Schritten, ganzen Tagen und Serien.

17 Abzeichen belohnen Schritte (1, 5, 10, 20, 50, 100, 150, 250, 500, 1000), ganze Tage (1, 10, 30) und Serien (3, 7, 14, 30 aufeinanderfolgende Kalendertage). Ganze Tage zählen ab Version 0.6.0 und benötigen mindestens einen geplanten Schritt sowie alle Schritte erledigt. Tage ohne Schritte oder mit offenen Schritten unterbrechen die Serie, sofern kein Pausentag geplant wurde; der laufende Tag hat bis Mitternacht Zeit. Frühere Tagespläne bleiben bei späteren Änderungen erhalten. Korrekturen aktualisieren die Serienwertung; verdiente Abzeichen bleiben erhalten und können von Eltern entzogen werden.

Eltern- und Kinderpasswörter benötigen mindestens 4 Zeichen. Datum und Uhrzeit folgen dem Gebietsschema des Browsers, mit ausgeschriebenen Monats- und Wochentagsnamen. Temperaturen werden als ganze Zahlen angezeigt.

Eine ruhige Routinen-App für Kinder und Eltern. Wusel läuft lokal auf Home Assistant OS auf einem Raspberry Pi 5 und wird über den Browser auf einem Tablet oder Smartphone bedient.

[English instructions](README.md)

## Funktionen

- Ein nächster Schritt mit großer **Erledigt**-Taste, optionaler Anleitung und kleinem Tageszähler.
- Ein schmaler Stufenbalken, kurze Punkterückmeldungen und eine kleine Feier bei einer neuen Stufe. „Bewegung reduzieren“ wird berücksichtigt.
- Checkliste und Abzeichen auf Wunsch. Eltern wählen die Startansicht jedes Kindes.
- Eigene Eltern- und Kinderkonten. Alle Eltern dieser Installation verwalten alle Kinder.
- Routinen für Wochentage, Wochenenden, jeden Tag oder ein bestimmtes Datum.
- Deutsch und Englisch sowie sechs persönliche Farbwelten: Wald, Ozean, Beere, Lavendel, Sonnenschein und Lagune (Petrol).
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

Übernimm alle neuen App-Dateien, einschließlich `server.py`, `Dockerfile` und `config.yaml`. Aktualisiere beziehungsweise baue die installierte App neu und prüfe Version **0.12.2**. Ein bloßer Neustart des alten Containers ändert den Netzwerkmodus noch nicht. Bei späteren Updates bleibt der Slug `wusel` unverändert.

Wusel teilt damit die Netzwerkschnittstellen des Pi. Dafür sind weder das Abschalten des Schutzmodus noch eine Portfreigabe am Router nötig. Die vorhandene Anmeldung und die Hinweise zu HTTP/HTTPS gelten weiterhin.

Technische Referenzen: [Waitress IPv4/IPv6-Listener](https://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html), [Home Assistant Host-Netzwerk](https://contributors.home-assistant.io/apps/reference/configuration/).

## Updates nach der Neuinstallation von 0.12.0

1. Erstelle ein Home Assistant Backup einschließlich Wusel und stoppe Wusel.
2. Suche Wusels bisherigen Quellordner im Ordner für lokale Apps. Benenne diesen bei Bedarf in `wusel` um und ersetze seine App-Dateien durch den Inhalt des neuen inneren Ordners `wusel`. Im überwachten App-Ordner soll nur eine Quellkopie dieser App liegen; sichere Quellkopien außerhalb davon.
3. Behalte bei Updates nach dieser Neuinstallation `slug: wusel` in `config.yaml` bei. Home Assistant identifiziert damit die App und ihre gespeicherten Daten.
4. Aktualisiere die Store-Liste, führe das Update beziehungsweise einen Rebuild aus und starte Wusel. Behalte die App währenddessen installiert, damit ihr Datenvolume erhalten bleibt.

Bei Updates dieser Installation bleiben Konten und Fortschritte in `/data/wusel.sqlite3` erhalten. Schemaanpassungen erfolgen automatisch.

Die Trennung von Ordner und Installationskennung beschreibt Home Assistant unter [How apps work](https://contributors.home-assistant.io/apps/how-apps-work/).

## Bedienung im Alltag

**Kinder:** Erledige den nächsten Schritt über **Erledigt**. **Meinen Tag ansehen** öffnet die Checkliste mit Rückgängig-Funktion. **Meine Abzeichen** öffnet die Belohnungen. Unter **Einstellungen** stehen Sprache, Farbwelt und Abmelden bereit. Antippen der Wetterzeile öffnet die Vorhersage.

**Eltern:** Unter **Familie** lassen sich Konten anlegen, Passwörter zurücksetzen und Startansichten wählen. Im **Wochenplan** werden Routinen erstellt oder bearbeitet. Unter **Prüfen** können Erledigungen zurückgenommen oder wiederhergestellt werden. **Abzeichen** erlaubt das Entfernen und Wiederherstellen von Abzeichen. Eltern wählen ihre Farben unter **Einstellungen**; Sprache und Abmelden stehen im Kontomenü oben rechts. Die Kinderauswahl steht direkt neben Übersicht, Wochenplan, Abzeichen und Prüfen; Familie und Einstellungen folgen in derselben Navigation. Überflüssige sichtbare Beschriftungen für Kind, Verwaltung, Sprache und Kontorolle entfallen; zugängliche Namen bleiben erhalten.

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
$env:WUSEL_DATA = Join-Path $PWD "work\dev-data"
$env:WUSEL_DEV = "1"
.\.venv\Scripts\python.exe .\wusel\app.py
```

Öffne `http://127.0.0.1:8099` und verwende den Einrichtungscode aus dem Terminal. Die lokale Entwicklung verwendet die Umgebungsvariablen `WUSEL_*`. Der Entwicklungsserver bindet nur an localhost; der Container verwendet Waitress.

## Prüfen und Paket erstellen

Im äußeren Projektordner:

```powershell
python -m pip install -r requirements-dev.txt
python tools/validate.py
python -m unittest discover -s tests -v
node tests/test_i18n.cjs
node tests/test_badge_view.cjs
python tools/package.py
python tools/validate.py --archive dist/wusel-0.12.2.zip
```

Das Paketwerkzeug schreibt `wusel-0.12.2.zip` in den Unterordner `dist` des Projekts. Im ZIP liegt die App-Konfiguration unter `wusel/wusel/config.yaml`. Lokale Daten, virtuelle Umgebungen und Bytecode werden nicht eingepackt.

Prüfungen und Grenzen stehen in [VALIDATION.md](../VALIDATION.md). Der Produktionsserver wurde lokal über IPv4 und IPv6 geprüft. Der neue Container-Netzwerkmodus, der Zugriff über den Hostnamen, Live-Wetter und Backup/Wiederherstellung müssen nach dem Update auf dem Pi überprüft werden.

## GitHub CI

Die [Pipeline](https://github.com/santsamu/wusel/actions/workflows/ci.yml) läuft bei Pull Requests, Pushes auf main und manuell. Sie prüft Python-/JavaScript-Tests, YAML/JSON, Versionen, Übersetzungen und die Integrität des Quellpakets. Danach baut und startet sie Container für AMD64 und ARM64 (ARM64 per QEMU), jeweils mit leeren temporären Daten. HTTP-Prüfungen decken Health-Endpunkt, Oberfläche, statische Dateien und Erststart-API ab. Das geprüfte ZIP steht 14 Tage als Actions-Artefakt bereit. Container werden nicht in eine Registry hochgeladen; am installierten Pi wird nichts geändert. Aktionen sind auf Commit-SHAs fixiert und verwenden nur Lesezugriff auf das Repository.

Korrekturen funktionieren in der Elternansicht unter Übersicht und Prüfen gleich: Schritt wieder öffnen zieht Punkte ab und wartet auf Erledigung bestätigen durch ein Elternteil. Auf der Kinderstartseite bleiben Titel, Uhrzeit und Hinweise des Schritts sichtbar.
