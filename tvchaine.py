from flask import Flask, render_template_string, request, redirect, jsonify, session
import mysql.connector
import requests
import tkinter as tk
from tkinter import ttk
import webbrowser

# =========================
# Fenêtre TV Chaînes
# =========================
def open_tvchaine_window(root):

    top = tk.Toplevel(root)
    top.title("TV Chaînes")
    top.geometry("1500x1300")
    top.configure(bg="#1e1e1e")

    # =========================
    # Titre
    # =========================
    label = tk.Label(
        top,
        text="Choisissez une chaîne TV :",
        font=("Arial", 18, "bold"),
        bg="#1e1e1e",
        fg="white"
    )
    label.place(x=500, y=150)

    # =========================
    # Dictionnaire des chaînes
    # =========================
    chaines = {

        # =========================
        # Chaînes classiques
        # =========================
        "TF1": {
            "web": "https://www.tf1.fr/",
            "vlc": ""
        },

        "France 2": {
            "web": "https://www.france.tv/france-2/",
            "vlc": ""
        },

        "France 3": {
            "web": "https://www.france.tv/france-3/",
            "vlc": ""
        },

        "France 4": {
            "web": "https://www.france.tv/france-4/",
            "vlc": ""
        },

        "France 5": {
            "web": "https://www.france.tv/france-5/",
            "vlc": ""
        },

        "Télé Congo": {
            "web": "https://telecongo.cg",
            "vlc": ""
        },

        "M6": {
            "web": "https://www.m6.fr/",
            "vlc": ""
        },

        "Arte": {
            "web": "https://www.arte.tv/en/",
            "vlc": ""
        },

        "C8": {
            "web": "https://www.canalplus.com/",
            "vlc": ""
        },

        "W9": {
            "web": "https://www.m6.fr/w9",
            "vlc": ""
        },

        "TMC": {
            "web": "https://www.tf1.fr/tmc",
            "vlc": ""
        },

        "TFX": {
            "web": "https://www.tf1.fr/tfx",
            "vlc": ""
        },

        "NRJ12": {
            "web": "https://www.nrj.fr/nrj-hits",
            "vlc": ""
        },

        "CStar": {
            "web": "https://www.cstar.fr",
            "vlc": ""
        },

        "LCI": {
            "web": "https://www.tf1info.fr/",
            "vlc": ""
        },

        "BFMTV": {
            "web": "https://www.bfmtv.com/",
            "vlc": ""
        },

        "TV5 Monde": {
            "web": "https://www.tv5monde.com/",
            "vlc": ""
        },

        # =========================
        # Streaming
        # =========================
        "Hotstar": {
            "web": "https://www.hotstar.com/",
            "vlc": ""
        },

        "Zee5": {
            "web": "https://www.zee5.com/global",
            "vlc": ""
        },

        "AfrolandTV": {
            "web": "https://www.afrolandtv.com/",
            "vlc": ""
        },

        "Nollyland": {
            "web": "https://www.nollyland.com",
            "vlc": ""
        },

        # =========================
        # Chaînes SPORT
        # =========================
        "beIN Sports": {
            "web": "https://www.beinsports.com/",
            "vlc": "http://example.com/beinsports.m3u8"
        },

        "Canal+ Sport": {
            "web": "https://www.canalplus.com/sport/",
            "vlc": "http://example.com/canalplussport.m3u8"
        },

        "RMC Sport": {
            "web": "https://rmcsport.bfmtv.com/",
            "vlc": "http://example.com/rmcsport.m3u8"
        },

        "DAZN": {
            "web": "https://www.dazn.com/",
            "vlc": "http://example.com/dazn.m3u8"
        },

        "FIFA TV": {
            "web": "https://www.fifa.com/fifaplus/",
            "vlc": "http://example.com/fifatv.m3u8"
        },

        "UEFA TV": {
            "web": "https://www.uefa.tv/",
            "vlc": "http://example.com/uefatv.m3u8"
        },

        "Premier League TV": {
            "web": "https://www.premierleague.com/",
            "vlc": "http://example.com/premierleague.m3u8"
        },

        "LaLiga TV": {
            "web": "https://www.laliga.com/",
            "vlc": "http://example.com/laliga.m3u8"
        },

        "Bundesliga TV": {
            "web": "https://www.bundesliga.com/",
            "vlc": "http://example.com/bundesliga.m3u8"
        },

        "CAF TV": {
            "web": "https://www.cafonline.com/",
            "vlc": "http://example.com/caftv.m3u8"
        },

        "SuperSport Football": {
            "web": "https://www.supersport.com/football",
            "vlc": "http://example.com/supersport.m3u8"
        },

        # =========================
        # Dessins animés GRATUITS
        # =========================
        "Pluto TV Kids": {
            "web": "https://pluto.tv/fr/live-tv",
            "vlc": "https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5f8ed946b1ce880007346c72/master.m3u8"
        },

        "Kidoodle TV": {
            "web": "https://www.kidoodle.tv/",
            "vlc": "https://example.com/kidoodletv.m3u8"
        }
    }

    # =========================
    # Combobox
    # =========================
    combo = ttk.Combobox(
        top,
        values=list(chaines.keys()),
        font=("Arial", 14),
        width=40,
        state="readonly"
    )

    combo.place(x=500, y=250)

    # Valeur par défaut
    combo.current(0)

    # =========================
    # Fonction ouvrir site web
    # =========================
    def ouvrir_chaine():

        nom = combo.get()

        if nom in chaines:
            url = chaines[nom]["web"]
            webbrowser.open(url)

    # =========================
    # Fonction lire VLC
    # =========================
    def lire_vlc():

        nom = combo.get()

        if nom in chaines:

            url_vlc = chaines[nom]["vlc"]

            if url_vlc != "":
                webbrowser.open(url_vlc)
            else:
                print("Aucun flux VLC disponible.")

    # =========================
    # Bouton ouvrir chaîne
    # =========================
    btn_open = tk.Button(
        top,
        text="Ouvrir la chaîne",
        command=ouvrir_chaine,
        bg="blue",
        fg="white",
        width=25,
        height=2,
        font=("Arial", 12, "bold")
    )

    btn_open.place(x=420, y=400)

    # =========================
    # Bouton VLC
    # =========================
    btn_vlc = tk.Button(
        top,
        text="Lire dans VLC",
        command=lire_vlc,
        bg="green",
        fg="white",
        width=25,
        height=2,
        font=("Arial", 12, "bold")
    )

    btn_vlc.place(x=750, y=400)

    # =========================
    # Bouton fermer
    # =========================
    btn_close = tk.Button(
        top,
        text="Fermer",
        bg="red",
        fg="white",
        width=20,
        height=2,
        command=top.destroy,
        font=("Arial", 12, "bold")
    )

    btn_close.place(x=600, y=520)

    return top