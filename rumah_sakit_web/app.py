from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'secret'

DATA_DOKTER_FILE = "dokter.json"
DATA_ANTRIAN_FILE = "antrian.json"

def load_data():
    if os.path.exists(DATA_DOKTER_FILE):
        with open(DATA_DOKTER_FILE, "r") as f:
            dokter_data = json.load(f)
    else:
        dokter_data = []

    if os.path.exists(DATA_ANTRIAN_FILE):
        with open(DATA_ANTRIAN_FILE, "r") as f:
            antrian_data = json.load(f)
    else:
        antrian_data = {}

    return dokter_data, antrian_data

def save_data():
    with open(DATA_DOKTER_FILE, "w") as f:
        json.dump(dokter_list, f, indent=2)
    with open(DATA_ANTRIAN_FILE, "w") as f:
        json.dump(antrian, f, indent=2)

dokter_list, antrian = load_data()

@app.route("/")
def index():
    return render_template("index.html", dokter_list=dokter_list)

@app.route("/tambah", methods=["GET", "POST"])
def tambah_dokter():
    if request.method == "POST":
        nama = request.form["nama"]
        spesialis = request.form["spesialis"]
        dokter_list.append({"nama": nama, "spesialis": spesialis})
        save_data()
        flash("Dokter berhasil ditambahkan!", "success")
        return redirect(url_for("index"))
    return render_template("tambah_dokter.html")

@app.route("/daftar/<nama_dokter>", methods=["GET", "POST"])
def daftar_pasien(nama_dokter):
    if request.method == "POST":
        nama_pasien = request.form["nama_pasien"]
        usia = request.form["usia"]
        pekerjaan = request.form["pekerjaan"]
        keluhan = request.form["keluhan"]

        if nama_dokter not in antrian:
            antrian[nama_dokter] = []
        # Simpan data pasien sebagai dict
        antrian[nama_dokter].append({
            "nama_pasien": nama_pasien,
            "usia": usia,
            "pekerjaan": pekerjaan,
            "keluhan": keluhan
        })
        save_data()
        flash(f"{nama_pasien} berhasil didaftarkan ke antrian!", "success")
        return redirect(url_for("daftar_pasien", nama_dokter=nama_dokter))

    pasien_list = antrian.get(nama_dokter, [])
    # Cari data dokter untuk ditampilkan (nama & spesialis)
    dokter_obj = next((d for d in dokter_list if d["nama"] == nama_dokter), None)

    return render_template("daftar_pasien.html", dokter=dokter_obj, pasien_list=pasien_list)

@app.route("/panggil/<nama_dokter>")
def panggil_pasien(nama_dokter):
    if nama_dokter in antrian and antrian[nama_dokter]:
        pasien_terpanggil = antrian[nama_dokter].pop(0)
        save_data()
        flash(f"Pasien {pasien_terpanggil['nama_pasien']} dipanggil!", "info")
    else:
        flash("Tidak ada pasien dalam antrian.", "warning")
    return redirect(url_for("daftar_pasien", nama_dokter=nama_dokter))

@app.route("/reset")
def reset_data():
    global dokter_list, antrian
    dokter_list = []
    antrian = {}
    save_data()
    flash("Data berhasil direset!", "warning")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
