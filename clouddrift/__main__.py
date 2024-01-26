import click

from clouddrift import adapters


@click.group()
def cli():
    pass

@cli.command(help="Download individual NetCDF files from the AOML server")
@click.option(
    "--drifter-ids", 
    type=str, 
    default=None, 
    help="List of drifter to retrieve (Default: all)"
)
@click.option(
    "--sample", 
    type=int,
    default=None, 
    help="Randomly select n_random_id drifter IDs to download (Default: None)"
)
@click.option(
    "--url", 
    type=str,
    default=adapters.gdp1h.GDP_DATA_URL, 
    help=f"URL from which to download the data (Default: {adapters.gdp1h.GDP_DATA_URL})"
)
@click.option(
    "--path", 
    type=click.Path(exists=False),
    default=adapters.gdp1h.GDP_TMP_PATH, 
    help=f"Path to the directory where the individual NetCDF files are stored (Default: {adapters.gdp1h.GDP_TMP_PATH})"
)
@click.option(
    "--experimental/--no-experimental", 
    default=False, 
    help=f"If true will instead use the experimental URL and tmp paths.This will override any values passed to url \
    and tmp-path (Default: False). Experimental values (url, path), \
    ({adapters.gdp1h.GDP_DATA_URL_EXPERIMENTAL}, {adapters.gdp1h.GDP_TMP_PATH_EXPERIMENTAL})"
)
def gdp1h(drifter_ids, sample, url, path, experimental):
    if experimental:
        url = adapters.gdp1h.GDP_DATA_URL_EXPERIMENTAL
        path = adapters.gdp1h.GDP_TMP_PATH_EXPERIMENTAL

    print(f"INPUTS:: \ndrifter-ids: {drifter_ids}\nsample: {sample}\nurl: {url}\ntmp_path: {path}\nexp: {experimental}")
    adapters.gdp1h.download(drifter_ids, sample, url, path)



if __name__ == "__main__":
    cli()