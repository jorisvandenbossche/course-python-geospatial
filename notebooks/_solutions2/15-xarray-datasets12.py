subset_mean = argo.sel(date=slice('2012-10-01', '2012-12-01')).mean(dim="date")