# -*- coding: utf-8 -*-
import os
import sys

from plugin.OpenAI import OpenAI

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))

if __name__ == "__main__":
    OpenAI()
