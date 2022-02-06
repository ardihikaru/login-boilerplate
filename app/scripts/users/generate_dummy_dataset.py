#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from app.scripts.users.generator import DummyUserDataGenerator

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num-users', type=int, default=20, help="Total number of users to be generated")
parser.add_argument('-e', '--export-path', type=str, default="dummy_users.json", help="Path to export json file")


def main():
    """ Main program """
    args = parser.parse_args()
    generator = DummyUserDataGenerator(args.num_users, args.export_path)
    generator.run()

    # # Opening JSON file
    # import json
    # json_file = open('dummy_users.json')
    # try load json
    # data = json.load(json_file)
    # print(data)


if __name__ == "__main__":
    main()
