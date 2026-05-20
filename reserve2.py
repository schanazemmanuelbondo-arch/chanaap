# =========================================================
# CHANAAPP TMDB FULL
# VERSION COMPLETE + VLC ADVANCED CONTROLS
# WINDOWS REDUCED + REPLAY BUTTON
# =========================================================

import os
import webbrowser
from datetime import datetime
from io import BytesIO
import threading
import time

import tkinter as tk
from tkinter import (
    ttk,
    filedialog,
    messagebox
)

import requests
import mysql.connector
from PIL import Image, ImageTk
import vlc

# =========================================================
# VLC CONFIG
# =========================================================

VLC_PATH = r"C:\Program Files\VideoLAN\VLC"

os.environ["PYTHON_VLC_MODULE_PATH"] = VLC_PATH

os.environ["PYTHON_VLC_LIB_PATH"] = os.path.join(
    VLC_PATH,
    "libvlc.dll"
)

# =========================================================
# TMDB API
# =========================================================

API_KEY = "12a16b82e676814cae1989b02766e57e"

BASE_URL = "https://api.themoviedb.org/3"

IMG_URL = "https://image.tmdb.org/t/p/w500"

# =========================================================
# DATABASE
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "netflixtmdb"
}

VIDEO_FOLDER = "videos"

DOWNLOAD_FOLDER = "downloads"

# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return mysql.connector.connect(**DB_CONFIG)

# =========================================================
# OPTIONAL TV MODULE
# =========================================================

try:

    import tvchaine

except ImportError:

    tvchaine = None

# =========================================================
# MAIN APP
# =========================================================

class MovieApp:

    def __init__(self, root):

        self.root = root

        self.root.title("chanaapp TMDB FULL")

        # FENETRE REDUITE
        self.root.geometry("1200x760")

        self.root.configure(bg="#1e1e1e")

        self.movies = []

        self.current_video = None

        self.is_dragging = False

        # =====================================================
        # VLC
        # =====================================================

        self.instance = vlc.Instance(
            "--no-video-title-show"
        )

        self.player = self.instance.media_player_new()

        # =====================================================
        # TITLE
        # =====================================================

        tk.Label(
            root,
            text="chanaapp TMDB FULL",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).place(
            relx=0.5,
            y=25,
            anchor="center"
        )

        # =====================================================
        # SEARCH LABEL
        # =====================================================

        tk.Label(
            root,
            text="Recherche Film",
            font=("Arial", 15, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).place(
            relx=0.5,
            y=80,
            anchor="center"
        )

        # =====================================================
        # SEARCH ENTRY
        # =====================================================

        self.search_entry = tk.Entry(
            root,
            width=50,
            font=("Arial", 12)
        )

        self.search_entry.place(
            relx=0.5,
            y=120,
            anchor="center"
        )

        # =====================================================
        # SEARCH BUTTON
        # =====================================================

        tk.Button(
            root,
            text="SEARCH",
            width=16,
            bg="blue",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.search_movies
        ).place(
            relx=0.5,
            y=165,
            anchor="center"
        )

        # =====================================================
        # MOVIES COMBOBOX
        # =====================================================

        tk.Label(
            root,
            text="Films Trouvés",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).place(
            relx=0.5,
            y=220,
            anchor="center"
        )

        self.movie_var = tk.StringVar()

        self.movie_combo = ttk.Combobox(
            root,
            textvariable=self.movie_var,
            width=55,
            state="readonly",
            font=("Arial", 11)
        )

        self.movie_combo.place(
            relx=0.5,
            y=260,
            anchor="center"
        )

        self.movie_combo.bind(
            "<<ComboboxSelected>>",
            self.show_movie_data
        )

        # =====================================================
        # PROVIDERS
        # =====================================================

        tk.Label(
            root,
            text="Providers",
            font=("Arial", 13, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).place(
            relx=0.5,
            y=320,
            anchor="center"
        )

        self.providers_listbox = tk.Listbox(
            root,
            width=55,
            height=8,
            font=("Arial", 10)
        )

        self.providers_listbox.place(
            relx=0.5,
            y=420,
            anchor="center"
        )

        self.providers_listbox.bind(
            "<<ListboxSelect>>",
            self.open_provider
        )

        # =====================================================
        # BUTTON FRAME
        # =====================================================

        btn_frame = tk.Frame(
            root,
            bg="#1e1e1e"
        )

        btn_frame.place(
            relx=0.5,
            y=660,
            anchor="center"
        )

        tk.Button(
            btn_frame,
            text="database videos",
            bg="blue",
            fg="white",
            width=16,
            font=("Arial", 10, "bold"),
            command=self.play_local_video
        ).grid(
            row=0,
            column=1,
            padx=10
        )

        tk.Button(
            btn_frame,
            text="TV Channels",
            bg="purple",
            fg="white",
            width=16,
            font=("Arial", 10, "bold"),
            command=self.open_tv
        ).grid(
            row=0,
            column=2,
            padx=10
        )

        tk.Button(
            btn_frame,
            text="Videos manager",
            bg="black",
            fg="white",
            width=16,
            font=("Arial", 10, "bold"),
            command=self.open_video_manager
        ).grid(
            row=0,
            column=3,
            padx=10
        )

    # =====================================================
    # SEARCH MOVIES
    # =====================================================

    def search_movies(self):

        query = self.search_entry.get().strip()

        if not query:

            messagebox.showwarning(
                "Erreur",
                "Entre un film"
            )

            return

        try:

            r = requests.get(
                f"{BASE_URL}/search/movie",
                params={
                    "api_key": API_KEY,
                    "query": query
                },
                timeout=10
            )

            data = r.json()

            self.movies = data.get(
                "results",
                []
            )

            titles = []

            for movie in self.movies:

                titles.append(
                    movie.get(
                        "title",
                        "Unknown"
                    )
                )

            self.movie_combo["values"] = titles

            if titles:

                self.movie_combo.current(0)

                self.show_movie_data()

            else:

                messagebox.showinfo(
                    "Info",
                    "Aucun film trouvé"
                )

        except Exception as e:

            messagebox.showerror(
                "Erreur API",
                str(e)
            )

    # =====================================================
    # GET MOVIE
    # =====================================================

    def get_movie(self):

        try:

            index = self.movie_combo.current()

            if index == -1:

                return None

            return self.movies[index]

        except Exception:

            return None

    # =====================================================
    # SHOW MOVIE DATA
    # =====================================================

    def show_movie_data(self, event=None):

        movie = self.get_movie()

        if not movie:
            return

        self.show_poster(movie)

        self.load_providers(movie)

    # =====================================================
    # SHOW POSTER
    # =====================================================

    def show_poster(self, movie):

        try:

            if hasattr(self, "poster_window"):

                if self.poster_window.winfo_exists():

                    self.poster_window.destroy()

            poster_path = movie.get(
                "poster_path"
            )

            if not poster_path:
                return

            url = IMG_URL + poster_path

            r = requests.get(url, timeout=10)

            img = Image.open(
                BytesIO(r.content)
            )

            # POSTER REDUIT
            img = img.resize((280, 420))

            self.poster_image = ImageTk.PhotoImage(img)

            self.poster_window = tk.Toplevel(
                self.root
            )

            self.poster_window.title(
                movie.get("title")
            )

            self.poster_window.geometry(
                "300x450"
            )

            self.poster_window.configure(
                bg="black"
            )

            lbl = tk.Label(
                self.poster_window,
                image=self.poster_image,
                bg="black"
            )

            lbl.pack()

        except Exception as e:

            print(e)

    # =====================================================
    # LOAD PROVIDERS
    # =====================================================

    def load_providers(self, movie):

        self.providers_listbox.delete(
            0,
            tk.END
        )

        try:

            r = requests.get(
                f"{BASE_URL}/movie/{movie['id']}/watch/providers",
                params={
                    "api_key": API_KEY
                },
                timeout=10
            ).json()

            results = r.get(
                "results",
                {}
            )

            country = results.get("FR")

            if not country:

                if results:
                    country = list(results.values())[0]

            if not country:

                self.providers_listbox.insert(
                    tk.END,
                    "No providers"
                )

                return

            providers = country.get(
                "flatrate",
                []
            )

            if not providers:

                self.providers_listbox.insert(
                    tk.END,
                    "No providers"
                )

                return

            self.current_provider_link = country.get(
                "link"
            )

            for provider in providers:

                self.providers_listbox.insert(
                    tk.END,
                    provider["provider_name"]
                )

        except Exception as e:

            messagebox.showerror(
                "Erreur Providers",
                str(e)
            )

    # =====================================================
    # OPEN PROVIDER
    # =====================================================

    def open_provider(self, event=None):

        try:

            if hasattr(
                self,
                "current_provider_link"
            ):

                webbrowser.open(
                    self.current_provider_link
                )

        except Exception as e:

            messagebox.showerror(
                "Erreur",
                str(e)
            )

    # =====================================================
    # CREATE PLAYER
    # =====================================================

    def create_player(self):

        try:

            if hasattr(self, "poster_window"):

                if self.poster_window.winfo_exists():

                    self.poster_window.destroy()

        except Exception:
            pass

        self.player_window = tk.Toplevel(
            self.root
        )

        self.player_window.title(
            "VLC PLAYER"
        )

        # FENETRE PLAYER REDUITE
        self.player_window.geometry(
            "900x620"
        )

        self.player_window.configure(
            bg="black"
        )

        # =====================================================
        # VIDEO FRAME
        # =====================================================

        self.video_frame = tk.Frame(
            self.player_window,
            bg="black"
        )

        self.video_frame.place(
            x=0,
            y=0,
            width=900,
            height=500
        )

        # =====================================================
        # CONTROLS
        # =====================================================

        controls = tk.Frame(
            self.player_window,
            bg="#222"
        )

        controls.place(
            x=0,
            y=500,
            width=900,
            height=120
        )

        # =====================================================
        # PROGRESS BAR VIDEO
        # =====================================================

        self.video_progress = ttk.Scale(
            controls,
            from_=0,
            to=100,
            orient="horizontal",
            length=700,
            command=self.set_video_position
        )

        self.video_progress.place(
            x=90,
            y=10
        )

        # =====================================================
        # TIME LABEL
        # =====================================================

        self.time_label = tk.Label(
            controls,
            text="00:00 / 00:00",
            fg="white",
            bg="#222",
            font=("Arial", 10, "bold")
        )

        self.time_label.place(
            x=390,
            y=40
        )

        # =====================================================
        # PLAY BUTTON
        # =====================================================

        tk.Button(
            controls,
            text="PLAY",
            width=10,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.resume_video
        ).place(
            x=20,
            y=75
        )

        # =====================================================
        # PAUSE BUTTON
        # =====================================================

        tk.Button(
            controls,
            text="PAUSE",
            width=10,
            bg="orange",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.pause_video
        ).place(
            x=130,
            y=75
        )

        # =====================================================
        # STOP BUTTON
        # =====================================================

        tk.Button(
            controls,
            text="STOP",
            width=10,
            bg="red",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.stop_video
        ).place(
            x=240,
            y=75
        )

        # =====================================================
        # REPLAY BUTTON
        # =====================================================

        tk.Button(
            controls,
            text="REPLAY",
            width=10,
            bg="#00aaff",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.replay_video
        ).place(
            x=350,
            y=75
        )

        # =====================================================
        # FORWARD BUTTON
        # =====================================================

        tk.Button(
            controls,
            text=">> +10s",
            width=10,
            bg="blue",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.forward_video
        ).place(
            x=460,
            y=75
        )

        # =====================================================
        # BACK BUTTON
        # =====================================================

        tk.Button(
            controls,
            text="<< -10s",
            width=10,
            bg="purple",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.backward_video
        ).place(
            x=570,
            y=75
        )

        # =====================================================
        # VOLUME
        # =====================================================

        tk.Label(
            controls,
            text="Volume",
            fg="white",
            bg="#222"
        ).place(
            x=710,
            y=60
        )

        self.volume_slider = ttk.Scale(
            controls,
            from_=0,
            to=100,
            orient="horizontal",
            length=150,
            command=self.change_volume
        )

        self.volume_slider.set(80)

        self.volume_slider.place(
            x=710,
            y=85
        )

        self.player_window.update()

        self.player.set_hwnd(
            self.video_frame.winfo_id()
        )

        self.player_window.protocol(
            "WM_DELETE_WINDOW",
            self.close_player
        )

        self.update_video_progress()

    # =====================================================
    # UPDATE VIDEO PROGRESS
    # =====================================================

    def update_video_progress(self):

        try:

            if self.player.is_playing():

                length = self.player.get_length()

                current = self.player.get_time()

                if length > 0:

                    progress = (current / length) * 100

                    self.video_progress.set(progress)

                    current_sec = int(current / 1000)

                    total_sec = int(length / 1000)

                    current_time = time.strftime(
                        '%H:%M:%S',
                        time.gmtime(current_sec)
                    )

                    total_time = time.strftime(
                        '%H:%M:%S',
                        time.gmtime(total_sec)
                    )

                    self.time_label.config(
                        text=f"{current_time} / {total_time}"
                    )

        except:
            pass

        if hasattr(self, "player_window"):

            if self.player_window.winfo_exists():

                self.player_window.after(
                    1000,
                    self.update_video_progress
                )

    # =====================================================
    # SET VIDEO POSITION
    # =====================================================

    def set_video_position(self, value):

        try:

            position = float(value) / 100

            self.player.set_position(position)

        except:
            pass

    # =====================================================
    # CHANGE VOLUME
    # =====================================================

    def change_volume(self, value):

        try:

            self.player.audio_set_volume(
                int(float(value))
            )

        except:
            pass

    # =====================================================
    # FORWARD VIDEO
    # =====================================================

    def forward_video(self):

        try:

            current = self.player.get_time()

            self.player.set_time(current + 10000)

        except Exception as e:

            messagebox.showerror(
                "Erreur",
                str(e)
            )

    # =====================================================
    # BACKWARD VIDEO
    # =====================================================

    def backward_video(self):

        try:

            current = self.player.get_time()

            new_time = current - 10000

            if new_time < 0:
                new_time = 0

            self.player.set_time(new_time)

        except Exception as e:

            messagebox.showerror(
                "Erreur",
                str(e)
            )

    # =====================================================
    # REPLAY VIDEO
    # =====================================================

    def replay_video(self):

        try:

            self.player.stop()

            self.player.play()

        except Exception as e:

            messagebox.showerror(
                "Erreur REPLAY",
                str(e)
            )

    # =====================================================
    # PLAY VIDEO FILE
    # =====================================================

    def play_video_file(self, file):

        try:

            if not os.path.exists(file):

                messagebox.showerror(
                    "Erreur",
                    f"Fichier introuvable :\n{file}"
                )

                return

            self.create_player()

            media = self.instance.media_new(
                os.path.abspath(file)
            )

            self.player.set_media(media)

            self.player.play()

            self.current_video = file

        except Exception as e:

            messagebox.showerror(
                "Erreur VLC",
                str(e)
            )

    # =====================================================
    # PLAY LOCAL VIDEO
    # =====================================================

    def play_local_video(self):

        try:

            conn = get_connection()

            cur = conn.cursor(
                dictionary=True
            )

            cur.execute("""
                SELECT * FROM videolocale
                ORDER BY id DESC
            """)

            videos = cur.fetchall()

            conn.close()

            if not videos:

                messagebox.showinfo(
                    "Info",
                    "Aucune video dans la base"
                )

                return

            select_window = tk.Toplevel(
                self.root
            )

            select_window.title(
                "Videos Locales"
            )

            # FENETRE REDUITE
            select_window.geometry(
                "620x420"
            )

            select_window.configure(
                bg="#1e1e1e"
            )

            listbox = tk.Listbox(
                select_window,
                width=70,
                height=15,
                font=("Arial", 10)
            )

            listbox.place(
                relx=0.5,
                y=180,
                anchor="center"
            )

            for video in videos:

                listbox.insert(
                    tk.END,
                    f"{video['id']} | {video['titre']}"
                )

            def play_selected():

                sel = listbox.curselection()

                if not sel:

                    messagebox.showerror(
                        "Erreur",
                        "Selectionne une vidéo"
                    )

                    return

                index = sel[0]

                video = videos[index]

                path = video["chemin_video"]

                select_window.destroy()

                self.play_video_file(path)

            tk.Button(
                select_window,
                text="LIRE VIDEO",
                bg="green",
                fg="white",
                width=18,
                font=("Arial", 10, "bold"),
                command=play_selected
            ).place(
                relx=0.5,
                y=380,
                anchor="center"
            )

        except Exception as e:

            messagebox.showerror(
                "Erreur DB",
                str(e)
            )

    # =====================================================
    # PLAY
    # =====================================================

    def resume_video(self):

        try:

            state = self.player.get_state()

            if state == vlc.State.Paused:

                self.player.pause()

            else:

                self.player.play()

        except Exception as e:

            messagebox.showerror(
                "Erreur PLAY",
                str(e)
            )

    # =====================================================
    # PAUSE
    # =====================================================

    def pause_video(self):

        try:

            self.player.pause()

        except Exception as e:

            messagebox.showerror(
                "Erreur PAUSE",
                str(e)
            )

    # =====================================================
    # STOP
    # =====================================================

    def stop_video(self):

        try:

            self.player.stop()

        except Exception as e:

            messagebox.showerror(
                "Erreur STOP",
                str(e)
            )

    # =====================================================
    # CLOSE PLAYER
    # =====================================================

    def close_player(self):

        try:

            self.player.stop()

        except:
            pass

        self.player_window.destroy()

    # =====================================================
    # OPEN TV
    # =====================================================

    def open_tv(self):

        if tvchaine:

            tvchaine.open_tvchaine_window(
                self.root
            )

        else:

            messagebox.showerror(
                "Erreur",
                "Module tvchaine absent"
            )

    # =====================================================
    # OPEN VIDEO MANAGER
    # =====================================================

    def open_video_manager(self):

        VideoManager(self.root)

# =========================================================
# VIDEO MANAGER
# =========================================================

class VideoManager:

    def __init__(self, root):

        self.root = root

        self.open()

    def open(self):

        self.top = tk.Toplevel(
            self.root
        )

        self.top.title(
            "Videos manager"
        )

        # FENETRE REDUITE
        self.top.geometry(
            "850x650"
        )

        self.top.configure(
            bg="#1e1e1e"
        )

        tk.Label(
            self.top,
            text="VIDEOS manager",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).place(
            relx=0.5,
            y=30,
            anchor="center"
        )

        self.video_var = tk.StringVar()

        self.combobox = ttk.Combobox(
            self.top,
            textvariable=self.video_var,
            width=45,
            state="readonly",
            font=("Arial", 11)
        )

        self.combobox["values"] = (
            "Videos Locales",
            "Films",
            "Series",
            "TV Chaînes"
        )

        self.combobox.current(0)

        self.combobox.place(
            relx=0.5,
            y=80,
            anchor="center"
        )

        self.combobox.bind(
            "<<ComboboxSelected>>",
            self.change_video
        )

        self.listbox = tk.Listbox(
            self.top,
            width=85,
            height=18,
            font=("Arial", 10)
        )

        self.listbox.place(
            relx=0.5,
            y=290,
            anchor="center"
        )

        # =====================================================
        # PROGRESS BAR
        # =====================================================

        self.progress = ttk.Progressbar(
            self.top,
            orient="horizontal",
            length=600,
            mode="determinate"
        )

        self.progress.place(
            relx=0.5,
            y=540,
            anchor="center"
        )

        self.progress_label = tk.Label(
            self.top,
            text="0%",
            fg="white",
            bg="#1e1e1e",
            font=("Arial", 10, "bold")
        )

        self.progress_label.place(
            relx=0.5,
            y=565,
            anchor="center"
        )

        btn_frame = tk.Frame(
            self.top,
            bg="#1e1e1e"
        )

        btn_frame.place(
            relx=0.5,
            y=610,
            anchor="center"
        )

        tk.Button(
            btn_frame,
            text="UPLOAD",
            bg="green",
            fg="white",
            width=18,
            font=("Arial", 10, "bold"),
            command=self.upload
        ).grid(
            row=0,
            column=0,
            padx=20
        )

        tk.Button(
            btn_frame,
            text="DOWNLOAD",
            bg="blue",
            fg="white",
            width=18,
            font=("Arial", 10, "bold"),
            command=self.download
        ).grid(
            row=0,
            column=1,
            padx=20
        )

        self.change_video()

    # =====================================================
    # CHANGE VIDEO
    # =====================================================

    def change_video(self, event=None):

        value = self.combobox.get()

        self.listbox.delete(
            0,
            tk.END
        )

        if value == "Videos Locales":

            self.load_local_videos()

    # =====================================================
    # LOAD VIDEOS
    # =====================================================

    def load_local_videos(self):

        try:

            conn = get_connection()

            cur = conn.cursor(
                dictionary=True
            )

            cur.execute("""
                SELECT * FROM videolocale
                ORDER BY id DESC
            """)

            videos = cur.fetchall()

            conn.close()

            for video in videos:

                self.listbox.insert(
                    tk.END,
                    f"{video['id']} | {video['titre']}"
                )

        except Exception as e:

            messagebox.showerror(
                "Erreur DB",
                str(e)
            )

    # =====================================================
    # UPDATE PROGRESS
    # =====================================================

    def update_progress(self, value):

        self.progress["value"] = value

        self.progress_label.config(
            text=f"{value}%"
        )

        self.top.update_idletasks()

    # =====================================================
    # UPLOAD
    # =====================================================

    def upload(self):

        file = filedialog.askopenfilename(
            title="Choisir une video",
            filetypes=[
                ("Videos", "*.mp4 *.mkv *.avi")
            ]
        )

        if not file:
            return

        threading.Thread(
            target=self.upload_thread,
            args=(file,)
        ).start()

    def upload_thread(self, file):

        try:

            os.makedirs(
                VIDEO_FOLDER,
                exist_ok=True
            )

            title = os.path.basename(file)

            destination = os.path.join(
                VIDEO_FOLDER,
                title
            )

            size = os.path.getsize(file)

            copied = 0

            with open(file, "rb") as src:

                with open(destination, "wb") as dst:

                    while True:

                        chunk = src.read(1024 * 1024)

                        if not chunk:
                            break

                        dst.write(chunk)

                        copied += len(chunk)

                        percent = int(
                            (copied / size) * 100
                        )

                        self.update_progress(percent)

            conn = get_connection()

            cur = conn.cursor()

            cur.execute("""
                INSERT INTO videolocale
                (
                    titre,
                    description,
                    chemin_video,
                    date_upload
                )
                VALUES (%s,%s,%s,%s)
            """, (
                title,
                "",
                destination,
                datetime.now()
            ))

            conn.commit()

            conn.close()

            messagebox.showinfo(
                "UPLOAD",
                "Upload terminé"
            )

            self.listbox.delete(0, tk.END)

            self.load_local_videos()

        except Exception as e:

            messagebox.showerror(
                "Erreur Upload",
                str(e)
            )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    def download(self):

        selection = self.listbox.curselection()

        if not selection:

            messagebox.showerror(
                "Erreur",
                "Selectionne une vidéo"
            )

            return

        line = self.listbox.get(
            selection[0]
        )

        video_id = line.split("|")[0].strip()

        threading.Thread(
            target=self.download_thread,
            args=(video_id,)
        ).start()

    def download_thread(self, video_id):

        try:

            conn = get_connection()

            cur = conn.cursor(
                dictionary=True
            )

            cur.execute(
                "SELECT * FROM videolocale WHERE id=%s",
                (video_id,)
            )

            video = cur.fetchone()

            conn.close()

            source = video["chemin_video"]

            os.makedirs(
                DOWNLOAD_FOLDER,
                exist_ok=True
            )

            destination = os.path.join(
                DOWNLOAD_FOLDER,
                os.path.basename(source)
            )

            size = os.path.getsize(source)

            copied = 0

            with open(source, "rb") as src:

                with open(destination, "wb") as dst:

                    while True:

                        chunk = src.read(1024 * 1024)

                        if not chunk:
                            break

                        dst.write(chunk)

                        copied += len(chunk)

                        percent = int(
                            (copied / size) * 100
                        )

                        self.update_progress(percent)

            messagebox.showinfo(
                "DOWNLOAD",
                f"Vidéo téléchargée :\n{destination}"
            )

        except Exception as e:

            messagebox.showerror(
                "Erreur Download",
                str(e)
            )

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = MovieApp(root)

    root.mainloop()