from pathlib import Path
import win32security
from tzlocal import get_localzone
import pandas as pd


def sizeof_fmt(num, suffix="B") -> str:
    for unit in [""] + "K M G T P E Z".split():
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"


def read_win32_owner(path: Path) -> str:
    sd = win32security.GetFileSecurity(
        str(path), win32security.OWNER_SECURITY_INFORMATION
    )
    owner_sid = sd.GetSecurityDescriptorOwner()
    name, domain, type = win32security.LookupAccountSid(None, owner_sid)
    return name


def dir_activity(target_dir: Path) -> pd.DataFrame:
    """
    Generate a detailed DataFrame of all files in the given target directory
    and its subdirectories.

    Parameters:
        target_dir (pathlib.Path): The target directory to search for files.

    Returns:
        pandas.DataFrame: A DataFrame containing the following columns:
            - path (str): The relative path of the file's parent directory.
            - fname (str): The name of the file.
            - size (int): The size of the file in bytes.
            - size_fmt (str): The formatted size of the file.
            - mtime (int): The modification time of the file as Unix timestamp.
            - mtime_fmt (str): The formatted modification time of the file.
            - owner (str): The owner of the file.

        The DataFrame is sorted by the 'mtime' column in descending order.
    """
    files = [
        {
            "path": str(f.relative_to(target_dir.parent).parent),
            "fname": f.name,
            "size": f.stat().st_size,
            "size_fmt": sizeof_fmt(f.stat().st_size),
            "mtime": f.stat().st_mtime,
            "mtime_fmt": pd.Timestamp.fromtimestamp(
                f.stat().st_mtime, tz=get_localzone()
            )
            .strftime("%#d%b%y %H:%M:%S %Z"),
            # 'owner': f.owner(),
            "owner": read_win32_owner(f),
        }
        for f in target_dir.rglob("*")
        if f.is_file()
    ]

    return pd.DataFrame(files).sort_values("mtime", ascending=False)


if __name__ == "__main__":
    print(dir_activity(Path.home() / "Downloads"))
