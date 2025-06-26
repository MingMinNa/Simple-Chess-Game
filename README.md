# Simple Chess Game

<a href="./README.md">English</a> | <a href="./README.zh-TW.md">繁體中文</a>

A simple chess game implemented with Python 3.12.9 and Pygame package.  
> The primary goal of this project is to gain hands-on experience with Python and the Pygame framework by creating a small game.

## Game Demo
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Initial Screen   
<img src="./assets/image/display/display_main.png" alt="display_main.png" width="254" height="200">


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Promotion&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Move Hint   
<img src="./assets/image/display/display_promotion.png" alt="display_promotion.png" width="285" height="200">
<img src="./assets/image/display/display_play.png" alt="display_play.png" width="285" height="200">

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Captured&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;End Panel   
<img src="./assets/image/display/display_captured.png" alt="display_captured.png" width="285" height="200">
<img src="./assets/image/display/display_end.png" alt="display_end.png" width="285" height="200">

## Environment
* Python version：`3.12.9`
* Package manager：`conda` / `pip`

## How to play
1. Create a Python 3.12 virtual environment and install required package.
    ```bash
    conda create -n <venv> python=3.12
    conda activate <venv>
    pip install -r requirements.txt
    ```
2. Run the main program
    ```bash
    python main.py
    ```
## Note
Most rules of chess, such as castling, en passant, and promotion, have been implemented, but a few draw conditions have not.
> The following draw rules have been implemented in the game:
> * [x] Stalemate
> * [x] Threefold repetition rule
> * [x] 50-move rule
>
> The following draw rules have NOT been implemented:
> * [ ] Insufficient material draw
> * [ ] Draw by agreement