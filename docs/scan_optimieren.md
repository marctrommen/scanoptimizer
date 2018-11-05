Scan optimieren
===============

1. Bild Scannen
   mit XSane Image Scanning bei Auflösung 300 DPI und Graustufen als einzelnes 
   PNG-Bild in Datei scannen

   1. Text-Scan optimieren

      [Optimieren mit ImageMagick](http://dikant.de/2013/05/01/optimizing-scanned-documents-with-imagemagick/)

      * bei überwiegend Text
        ```
        $> mogrify -normalize -level 10%,90% -sharpen 0x1 scan_a.png
        ```
      * bei überwiegend Bild
        ```
        $> mogrify -normalize -level 15%,85% scan_a.png
        ```
      Tipp: je Bild den Aufruf mehrmals durchführen (z.B. 7x)

   2. Cleaning scanned grayscale images with ImageMagick
      [Graustufenbilder säubern](https://stackoverflow.com/questions/9608279/cleaning-scanned-grayscale-images-with-imagemagick)

2. mehrere Bilder in ein PDF-Dokument konvertieren
   [JPEG zu PDF konvertieren](https://askubuntu.com/questions/246647/jpeg-files-to-pdf)
   ```
   $> convert scan_a.png scan_b.png scan_c.png scan.pdf
   ```

Weitere Tipps
-------------

https://rohieb.name/blag/post/optimizing-xsane-s-scanned-pdfs/
http://blog.konradvoelkel.de/2013/03/scan-to-pdfa/

```
scanimage
'hpaio:/usb/Officejet_Pro_8600?serial=CN2C1CXJGN05KC'

Options specific to device `hpaio:/usb/Officejet_Pro_8600?serial=CN2C1CXJGN05KC':
  Scan mode:
    --mode Lineart|Gray|Color [Lineart]
        Selects the scan mode (e.g., lineart, monochrome, or color).
    --resolution 75|100|200|300dpi [75]
        Sets the resolution of the scanned image.
    --source Flatbed|ADF [Flatbed]
        Selects the scan source (such as a document-feeder).
  Advanced:
    --brightness 0..2000 [1000]
        Controls the brightness of the acquired image.
    --contrast 0..2000 [1000]
        Controls the contrast of the acquired image.
    --compression JPEG [JPEG]
        Selects the scanner compression method for faster scans, possibly at
        the expense of image quality.
    --jpeg-quality 0..100 [inactive]
        Sets the scanner JPEG compression factor. Larger numbers mean better
        compression, and smaller numbers mean better image quality.
  Geometry:
    -l 0..215.9mm [0]
        Top-left x position of scan area.
    -t 0..297.011mm [0]
        Top-left y position of scan area.
    -x 0..215.9mm [215.9]
        Width of scan-area.
    -y 0..297.011mm [297.011]
        Height of scan-area.
```

Type `$> scanimage --help -d DEVICE` to get list of all options for DEVICE.

für Bilder 13cm x 9cm farbig scannen:
```
$> scanimage --mode Color --resolution 300 --format tiff -x 130 -y 90 > test.tiff
$> convert test.tiff test.png
$> mogrify -normalize -level 5%,95% test.png
```

https://linux.die.net/man/1/scanimage
http://www.linuxdevcenter.com/pub/a/linux/2000/07/18/LivingLinux.html

```
$> scanimage --test -d 'hpaio:/usb/Officejet_Pro_8600?serial=CN2C1CXJGN05KC'
```
