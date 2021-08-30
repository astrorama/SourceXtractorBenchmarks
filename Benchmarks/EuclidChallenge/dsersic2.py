from glob import glob
import numpy as np
from sourcextractor.config import *

top = load_fits_images(sorted(glob('dsersic_2_vis.fits')),
                       psfs=sorted(glob('dsersic_2_vis.psf')),
                       weights=sorted(glob('dsersic_2_vis.rms.fits')),
                       weight_type='rms')

mesgroup = MeasurementGroup(top)

MAG_ZEROPOINT = 23.9

rad = FreeParameter(lambda o: o.get_radius(), Range(lambda v, o: (.01 * v, 30 * v), RangeType.EXPONENTIAL))

e1 = FreeParameter(0.0, Range((-0.9999, 0.9999), RangeType.LINEAR))
e2 = FreeParameter(0.0, Range((-0.9999, 0.9999), RangeType.LINEAR))
emod = DependentParameter(lambda x, y: np.sqrt(x * x + y * y), e1, e2)
angle = DependentParameter(lambda e1, e2: 0.5 * np.arctan2(e1, e2), e1, e2)
ratio = DependentParameter(lambda e: (1 - e) / (1 + e), emod)
add_prior(e1, 0.0, 0.3)
add_prior(e2, 0.0, 0.3)

sersic = FreeParameter(2.0, Range((0.3, 8.0), RangeType.LINEAR))
X_sersic = DependentParameter(lambda n: np.log((n - 0.25) / (10 - n)), sersic)
add_prior(X_sersic, -0.8, 1.5)

x, y = get_pos_parameters()
ra, dec = get_world_position_parameters(x, y)
flux = get_flux_parameter()
mag = DependentParameter(lambda f: -2.5 * np.log10(f) + MAG_ZEROPOINT, flux)

add_model(mesgroup, SersicModel(x, y, flux, rad, ratio, angle, sersic))

add_output_column('x', x)
add_output_column('y', y)
add_output_column('ra', ra)
add_output_column('dec', dec)
add_output_column('mag', mag)
add_output_column('rad', rad)
add_output_column('ratio', ratio)
add_output_column('angle', angle)
add_output_column('e1', e1)
add_output_column('e2', e2)
add_output_column('emod', emod)
add_output_column('sersic', sersic)
add_output_column('X_sersic', X_sersic)
