# Rigenera i file in export/ a partire da cad/mx_led.scad.
# I target non partono da soli: lanciali uno per volta (make stl, make obj, ...).

OPENSCAD ?= openscad
PY       ?= uv run --quiet --with pillow --with numpy python3

SCAD  := cad/mx_led.scad
LOGO  := cad/logo_pts.scad
PARTS := core_left core_right plate_left plate_right plate_left_white plate_right_white \
         cap pins spacers test_core test_plate test_plate_white
STLS  := $(PARTS:%=export/stl/mx_%.stl)

.PHONY: help logo stl obj dima render
help:
	@echo "make logo    cad/logo_pts.scad da cad/MX_black.svg"
	@echo "make stl     tutti gli STL in export/stl/ (i corpi con CGAL ci mettono parecchio)"
	@echo "make export/stl/mx_plate_left.stl   un pezzo solo"
	@echo "make obj     OBJ multicolore delle lastre in export/obj/"
	@echo "make dima    dima A3 delle viti in export/dima/"
	@echo "make render  fotoinserimenti sul muro in tools/render/out/"

logo:
	python3 tools/svg2pts.py cad/MX_black.svg $(LOGO)

stl: $(STLS)

export/stl/mx_%.stl: $(SCAD) $(LOGO)
	$(OPENSCAD) -D 'part="$*"' -o $@ $(SCAD)

obj: export/stl/mx_plate_left.stl export/stl/mx_plate_right.stl \
     export/stl/mx_plate_left_white.stl export/stl/mx_plate_right_white.stl
	python3 tools/make_obj.py

dima:
	$(PY) tools/make_dima.py

render:
	mkdir -p tools/render/out
	$(PY) tools/render/render.py tools/render/out
