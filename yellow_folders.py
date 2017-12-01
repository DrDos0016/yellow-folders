import argparse
import glob
import os
import subprocess
import shutil
import sys

from zipfile import ZipFile
from datetime import datetime

DIRECTORIES = [
    "1991", "1992", "1993", "1994", "1995", "1996", "1997",
    "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005",
    "2006", "2007", "2008", "2009", "201X", "unknown", "utilities", "superz",
    "zig", "projects", "shared", "temp"
    ]


def create_directory_structure():
    """ Creates directories defined in DIRECTORIES """
    print("Creating directory structure.")
    for directory in DIRECTORIES:
        if not os.path.isdir(directory):
            os.mkdir(directory)


def copy_shared_files():
    print("Copying shared files into necessary directories...")
    return True


def extract_mass_zips():
    """ Locate an unzip the contents of the ZZT mass zip files """
    zips = glob.glob("*.[Zz][Ii][Pp]")
    zips.sort()

    for zipname in zips:
        print("Extracting contents of", zipname)
        directory = zipname.replace("zzt_worlds_", "")[:-4]

        if directory.startswith("2010-"):
            directory = "201X"
        elif directory.startswith("szzt"):
            directory = "superz"
        elif directory.startswith("zig"):
            directory = "zig"
        elif directory.startswith("UNKNOWN"):
            directory = "unknown"
        elif directory.startswith("utilities"):
            directory = "utilities"

        unzip(zipname, directory)
    return zips


def get_md5(file_path):
    """ Return the md5 checksum of a file """
    resp = subprocess.run(["md5sum", file_path], stdout=subprocess.PIPE)
    checksum = resp.stdout[:32].decode("utf-8")
    return checksum


def reset():
    """ Debug function to erase all files (except for the shared folder) """
    input("Press enter to ERASE ALL DIRECTORIES (excluding shared)")
    for directory in DIRECTORIES:
        if directory != "shared" and os.path.isdir(directory):
            shutil.rmtree(directory)


def unzip(zipname, directory):
    with ZipFile(zipname) as zf:
        zf.extractall(path=directory)

    world_zips = glob.glob(os.path.join(directory, "*.[Zz][Ii][Pp]"))

    for world_zip in world_zips:
        try:
            with ZipFile(world_zip) as zf:
                # Contents to extract is blank, destination is main folder
                contents = []
                destination = directory

                # Figure out what to extract and where
                for f in zf.infolist():
                    file_path = os.path.join(directory, f.filename)
                    if not os.path.isfile(file_path):
                        contents.append((f, f.filename))  # Keep original name
                    else:  # Handle duplicate filenames
                        # For ZZT files, compare md5s
                        if os.path.basename(file_path).upper().endswith(".ZZT"):

                            # Already extracted file
                            md5_a = get_md5(file_path)

                            # Temp extract the file in question
                            zf.extract(f, path="temp")
                            md5_b = get_md5(os.path.join("temp", f.filename))
                            os.remove(os.path.join("temp", f.filename))

                            # If the md5 is different, use dupes
                            if md5_a != md5_b:
                                destination = "dupe"

                            contents.append((f, f.filename))
                        # For non-ZZT files, rename them with the zip file as a
                        # prefix
                        else:
                            extended_name = os.path.splitext(
                                os.path.basename(world_zip)
                            )[0] + "-" + f.filename
                            contents.append((f, extended_name))

                # Actually extract files to the proper directory
                if destination == "dupe":
                    output_directory = os.path.join(directory, "dupe")
                    # Create the dupe folder if it doesn't exist
                    if not os.path.isdir(output_directory):
                        os.mkdir(output_directory)

                else:
                    output_directory = directory

                for f in contents:
                    zip_name = f[0]
                    zip_name.filename = f[1]
                    # Dupes within dupes...
                    if (
                       os.path.basename(
                        zip_name.filename
                       ).upper().endswith(".ZZT") and os.path.isfile(
                        os.path.join(zip_name.filename, output_directory)
                       )):
                        print("DUPE WITHIN DUPES!")

                    zf.extract(zip_name, path=output_directory)

            os.remove(os.path.join(world_zip))
        except NotImplementedError:
            print("\tINVALID ZIP FORMAT FOR", world_zip)
        except (OSError, IndexError):
            print("\tINVALID ZIP CONTENT FOR", world_zip)
        except:
            print("\tUNKNOWN ERROR FOR", world_zip)


def main():
    parser = argparse.ArgumentParser(
        description="Yellow Folders - A ZZT file structuring system"
    )

    parser.add_argument("--reset", action="store_true", default="False")

    args = parser.parse_args()

    if args.reset is True:
        reset()

    create_directory_structure()
    extract_mass_zips()
    copy_shared_files()

    return True


if __name__ == "__main__":
    main()
