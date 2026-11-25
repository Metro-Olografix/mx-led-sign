// ============================================================================
//  Logo MX da esterno con striscia WS2812B laterale
//  Stampante: Elegoo Centauri Carbon 2 (piatto 256 x 256)
//
//  Ogni meta' del logo e' fatta di due pezzi:
//   - corpo  (retro + anima + labbro posteriore), stampato col retro sul piatto
//   - lastra frontale da 4 mm (+ labbro anteriore), stampata col fronte sul piatto
//  Cosi' la gola laterale non ha sbalzi nel vuoto. Niente viti tra i pezzi:
//  i due corpi si incastrano a coda di rondine (il destro scende dall'alto nel
//  sinistro); le lastre, con la giunta sfalsata di 15 mm, si centrano con
//  spine di centraggio (stampate a parte) e sono serrate contro il muro dalle due viti a muro, che premono sulla
//  lastra. Svitate quelle, la lastra si sfila e si puo' cambiare la striscia.
//  La striscia LED corre nella gola sul fianco del corpo, su tutto il contorno.
//  Il diffusore e' stampato insieme alla lastra (multicolore: piastra nera +
//  parte bianca con parete del diffusore, labbro anteriore e pioli, cosi' il
//  colore cambia una volta sola): chiudendo la lastra la parete scende nella
//  gola davanti alla striscia, dietro al labbro del corpo.
//  Il controller sta fuori dal logo: il cavo scende dall'alto ed entra da una
//  tacca sul bordo superiore, dove la striscia inizia e finisce.
//  Fissaggio: le 2 viti gia' presenti nel muro (interasse 238 mm) passano dal
//  fronte attraverso la fine della gamba sinistra della M e la punta del braccio
//  in alto a destra della X; le teste si coprono con due tappini neri.
//  Le posizioni delle viti valgono solo per logo_width = 260.
//
//  I CORPI SONO GIA' STAMPATI: non cambiare i parametri della gola, dei pioli,
//  della coda di rondine e delle viti, o le lastre nuove non combaciano piu'.
//
//  Coordinate di progetto: z = 0 retro, z = T fronte (il logo si legge da +z).
//  Ogni parte esportata e' gia' orientata per la stampa. Le parti "_white"
//  hanno le stesse coordinate della lastra nera (vedi make_obj.py).
//
//  Export:  openscad -D 'part="plate_right"' -o plate_right.stl mx_led.scad
// ============================================================================

include <logo_pts.scad>

/* [Parte da generare] */
part = "assembly"; // [assembly, core_left, core_right, plate_left, plate_right, plate_left_white, plate_right_white, cap, pins, spacers, test_core, test_plate, test_plate_white]

/* [Logo] */
logo_width   = 260;   // larghezza totale [mm] (le viti a muro sono calcolate per 260)
cut_x        = logo_width / 2;   // taglio tra i due corpi [mm]
plate_cut_x  = cut_x + 15;       // taglio tra le due lastre frontali (sfalsato)
front_wall   = 4;     // spessore lastra frontale
back_wall    = 7.4;   // materiale tra gola e retro

/* [Striscia LED] */
strip_type   = "IP67"; // [IP30, IP65, IP67]
lip_d        = 0.8;    // sporgenza dei labbri che trattengono la striscia
lip_t        = 0.8;    // spessore dei labbri
feed_x       = 100 * logo_width / 300;  // posizione (x) della tacca d'ingresso cavo sul bordo superiore
feed_w       = 8;      // larghezza tacca (fili + capi della striscia)
feed_depth   = 12;     // quanto la tacca entra nel logo dal bordo superiore

/* [Gola dei corpi gia' stampati - non cambiare] */
diffuser     = true;
diff_back    = 1.2;
diff_clear   = 0.1;

/* [Diffusore integrato nella lastra] */
skirt_t      = 0.8;    // spessore parete bianca (2 passate). Gioco davanti alla striscia: vedi echo
skirt_clear  = 0.15;   // gioco tra il fondo della parete e il fondo della gola
skirt_key    = 1.0;    // quanto la parete bianca affonda nella piastra nera (incastro)

/* [Coda di rondine e pioli] */
dt_neck      = 9;     // coda di rondine tra i corpi: larghezza al collo (> anima, niente pareti sottili)
dt_tip       = 13;    // larghezza in fondo
dt_len       = 8;     // profondita'
dt_fit       = 0.15;  // gioco per lato
peg_d        = 4;     // fori per le spine lastra -> corpo (nel corpo gia' stampato: 4,05 x 3,5 mm)
peg_h        = 3;     // profondita' del foro nel corpo (piu' 0,5 di margine)
pin_d        = 3.9;   // spina separata, stampata sdraiata (o spina d'acciaio 4x6)
pin_len      = 6;
plate_hole   = 3;     // profondita' del foro nella lastra (resta 1 mm pieno sul fronte)
press_fit    = 0.05;  // gioco dei fori per i pioli a pressione (anche distanziali)

/* [Fissaggio a muro] */
standoff     = 10;    // distanza retro-muro (distanziali)
foot_r       = 7;
wall_screws  = [[10.75, 89.75], [248.75, 89.75]];  // viti esistenti, interasse 238 mm (logo da 260)
wscrew_d     = 3.4;   // foro passante per la vite da 3 mm
cbore_d      = 7.5;   // sede della testa (7 mm)
cap_t        = 0.8;   // spessore tappino
head_h       = 2.0;   // altezza testa della vite a muro
fit          = 0.2;   // gioco del perno dei distanziali delle viti

/* [Hidden] */
$fn  = 48;
eps  = 0.01;
S    = logo_width / LOGO_W;
H    = LOGO_H * S;
k300 = logo_width / 300;   // coordinate scritte per il logo a 300 mm

// [larghezza, spessore] nominali della striscia (dalla scheda prodotto)
strip    = strip_type == "IP67" ? [12, 3.85] : strip_type == "IP65" ? [10, 3] : [10, 2];
groove_h = strip[0] + 0.6;                   // altezza gola
diff_t   = diffuser ? diff_back + diff_clear : 0;
groove_d = lip_d + diff_t + strip[1] + 0.15; // profondita' della gola
T        = front_wall + groove_h + back_wall;

g0 = back_wall;              // quota inferiore gola
g1 = back_wall + groove_h;   // quota superiore gola = piano di appoggio della lastra

// centro della barra alta nel punto di taglio
bar_y = 173.08 * k300;

// distanziali extra: tengono il logo parallelo al muro
feet = [ for (f = [[17.5, 166.8], [103.9, 108.0], [191.1, 166.0], [287.1, 13.0], [196.5, 11.9]]) f * k300 ];
// pioli della lastra (coordinate per il logo da 260, sull'asse dei tratti)
plate_pegs = [[34.7, 150.0], [62.4, 150.0], [90.0, 108.3], [10.0, 104.0],
              [169.3, 112.7], [209.7, 49.4], [189.05, 33.65], [230.7, 34.05]];

// zona del pezzo di prova: fine della gamba sinistra (curva + tratti dritti + vite + piolo)
test_box = [[-5, 70], [25, 112]];

// ---------------------------------------------------------------- 2D
module logo2d() scale([S, S]) polygon(LOGO_PTS);

// fascia tra il bordo rientrato di a e quello rientrato di b
module band(a, b) difference() {
    if (a == 0) logo2d(); else offset(delta = -a) logo2d();
    offset(delta = -b) logo2d();
}

// ---------------------------------------------------------------- corpo e lastra
// Costruiti separatamente (niente tagli su piani coincidenti con la gola).

module feed_cut() {
    // tacca aperta sul retro e sul bordo superiore, collegata alla gola
    translate([feed_x - feed_w/2, H - feed_depth, -eps])
        cube([feed_w, feed_depth + 5, g0 + 3]);
}

module core_all() difference() {
    linear_extrude(g1) logo2d();
    // gola: fascia piena sopra il labbro posteriore + zona dietro al labbro
    translate([0, 0, g0 + lip_t]) linear_extrude(groove_h)
        difference() { offset(delta = 5) logo2d(); offset(delta = -groove_d) logo2d(); }
    translate([0, 0, g0]) linear_extrude(groove_h) band(lip_d, groove_d);
    feed_cut();
    for (w = wall_screws) translate([w[0], w[1], 0]) {
        translate([0, 0, -1]) cylinder(d = wscrew_d, h = g1 + 2);
        translate([0, 0, -eps]) cylinder(d = 6 + 2*fit, h = 2);       // sede del perno del distanziale
    }
    for (f = feet) translate([f[0], f[1], -eps]) cylinder(d = 5 + press_fit, h = 4.5);
    for (p = plate_pegs) translate([p[0], p[1], g1 - peg_h - 0.5]) cylinder(d = peg_d + press_fit, h = peg_h + 1);
}

// lastra nera: solo la piastra. Labbro e pioli sono nella parte bianca (vedi
// plate_white_all), cosi' sopra la piastra si stampa un colore solo.
module plate_all() difference() {
    translate([0, 0, g1]) linear_extrude(front_wall) logo2d();
    // fori per le spine di centraggio (la spina si incolla qui)
    for (p = plate_pegs) translate([p[0], p[1], g1 - eps]) cylinder(d = peg_d + 0.1, h = plate_hole + eps);
    // scanalatura in cui affonda la parete bianca (la tiene anche di fianco)
    translate([0, 0, g1 - eps]) linear_extrude(skirt_key + eps) band(lip_d + 0.05, lip_d + 0.05 + skirt_t);
    // vite a muro: la testa preme sulla lastra (sotto restano front_wall - head_h - cap_t mm)
    for (w = wall_screws) translate([w[0], w[1], 0]) {
        translate([0, 0, g1 - 1]) cylinder(d = wscrew_d, h = front_wall + 2);
        translate([0, 0, T - head_h - cap_t]) cylinder(d = cbore_d, h = 5);
    }
}

module side_box(side, x) translate(side == "left" ? [-50, -50, -100] : [x, -50, -100])
    cube(side == "left" ? [x + 50, H + 100, 200] : [500, H + 100, 200]);

// coda di rondine sulla barra alta: il maschio sporge dal corpo destro dentro al sinistro
module dovetail(grow = 0) translate([0, 0, -1]) linear_extrude(g1 + 2)
    offset(delta = grow) polygon([[cut_x + 0.5, bar_y - dt_neck/2], [cut_x - dt_len, bar_y - dt_tip/2],
                                  [cut_x - dt_len, bar_y + dt_tip/2], [cut_x + 0.5, bar_y + dt_neck/2]]);

module core_half(side) intersection() {
    core_all();
    if (side == "left") difference() { side_box("left", cut_x); dovetail(dt_fit); }
    else union() { side_box("right", cut_x); dovetail(0); }
}

module plate_half(side) intersection() { plate_all(); side_box(side, plate_cut_x); }

// ---------------------------------------------------------------- parte bianca della lastra
// Parete del diffusore appesa sotto la lastra, appena dietro al labbro: scende
// fino a skirt_clear dal fondo della gola, passando dietro al labbro del corpo.
module skirt_all() translate([0, 0, g0 + skirt_clear]) linear_extrude(g1 - g0 - skirt_clear + skirt_key)
    band(lip_d + 0.05, lip_d + 0.05 + skirt_t);

// tutto cio' che sta sotto la piastra e' bianco: diffusore e labbro anteriore
module plate_white_all() {
    skirt_all();
    translate([0, 0, g1 - lip_t]) linear_extrude(lip_t) band(0, lip_d + 0.1);
}

module skirt_half(side) intersection() { plate_white_all(); side_box(side, plate_cut_x); }

// ---------------------------------------------------------------- accessori
// spina di centraggio stampata sdraiata (strati lungo l'asse: non si spezza),
// con una faccia piana per il piatto e smussi alle estremita'
module pin() difference() {
    translate([0, 0, pin_d/2 - 0.3]) rotate([0, 90, 0]) hull() {
        cylinder(d = pin_d - 0.6, h = pin_len, center = true);
        cylinder(d = pin_d, h = pin_len - 0.6, center = true);
    }
    translate([0, 0, -5]) cube([pin_len + 2, 10, 10], center = true);
}

module cap() {
    // tappino da incollare (silicone) sopra la testa della vite
    cylinder(d1 = cbore_d - 0.6, d2 = cbore_d - 0.25, h = 0.4);
    translate([0, 0, 0.4]) cylinder(d = cbore_d - 0.25, h = cap_t - 0.4);
}

// distanziale per le viti: tubo col perno che centra nel retro
module spacer_screw() difference() {
    union() {
        cylinder(r = foot_r, h = standoff);
        translate([0, 0, standoff - eps]) cylinder(d = 6, h = 1.8);
    }
    translate([0, 0, -1]) cylinder(d = wscrew_d, h = standoff + 4);
}

// distanziale semplice: entra a pressione nel foro sul retro
module spacer_foot() {
    cylinder(r = foot_r, h = standoff);
    translate([0, 0, standoff - eps]) cylinder(d = 5, h = 4);
}

// striscia, solo per l'anteprima (appoggiata sul fondo della gola)
module strip_ghost() {
    translate([0, 0, g0 + (groove_h - strip[0])/2]) linear_extrude(strip[0])
        band(groove_d - 0.15 - strip[1], groove_d - 0.15);
}

module test_clip() translate([test_box[0][0], test_box[0][1], -50])
    cube([test_box[1][0] - test_box[0][0], test_box[1][1] - test_box[0][1], 100]);

// ---------------------------------------------------------------- uscita
module print_flip() translate([0, 0, T]) rotate([0, 180, 0]) children();

echo(str("Viti a muro: attraversano ", T - head_h - cap_t + standoff, " mm di plastica + la parte nel tassello"));
echo(str("Diffusore: parete ", skirt_t, " mm; gioco davanti alla striscia ",
          groove_d - 0.15 - strip[1] - (lip_d + 0.05 + skirt_t), " mm"));
echo(str("Striscia ", strip_type, ": gola ", groove_h, " x ", groove_d, " mm, spessore logo T = ", T, " mm"));

if (part == "assembly") {
    color("dimgray") { core_half("left"); core_half("right"); }
    color("gray") translate([0, 0, 0.3]) { plate_half("left"); plate_half("right"); }
    color("orange") strip_ghost();
    color("white") translate([0, 0, 0.3]) { skirt_half("left"); skirt_half("right"); }
    color("darkslategray") {
        for (w = wall_screws) translate([w[0], w[1], -standoff]) spacer_screw();
        for (f = feet) translate([f[0], f[1], -standoff]) spacer_foot();
    }
}
else if (part == "core_left")         core_half("left");
else if (part == "core_right")        core_half("right");
else if (part == "plate_left")        print_flip() plate_half("left");
else if (part == "plate_right")       print_flip() plate_half("right");
else if (part == "plate_left_white")  print_flip() skirt_half("left");
else if (part == "plate_right_white") print_flip() skirt_half("right");
else if (part == "cap")               for (i = [0:3]) translate([i*10, 0, 0]) cap();
else if (part == "pins")              for (i = [0:9]) translate([(i % 5) * 9, floor(i / 5) * 6, 0]) pin();
else if (part == "spacers") {
    for (i = [0:len(wall_screws) - 1]) translate([i*18, 0, 0]) spacer_screw();
    for (i = [0:len(feet) - 1]) translate([i*18, 18, 0]) spacer_foot();
}
else if (part == "test_core")         intersection() { core_all(); test_clip(); }
else if (part == "test_plate")        print_flip() intersection() { plate_all(); test_clip(); }
else if (part == "test_plate_white")  print_flip() intersection() { plate_white_all(); test_clip(); }
