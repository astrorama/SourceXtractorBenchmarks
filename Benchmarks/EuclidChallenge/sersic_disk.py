from glob import glob
import numpy as np
from sourcextractor.config import *

# read out the field name
args = Arguments(act_field="field_0")
act_field=args.act_field

# define the data location
data_file_path = '../../DEEPFIELD/FIELD%s/Double_Sersic/dsersic_%s_vis.fits' % (act_field, act_field)
rms_file_path  = '../../DEEPFIELD/FIELD%s/Double_Sersic/dsersic_%s_vis.rms.fits' % (act_field, act_field)

# load the image
top = load_fits_images(
    sorted(glob(data_file_path)),
    weights=sorted(glob(rms_file_path)),
    weight_type='rms',
    constant_background = 0.0,
    weight_absolute=1,
    psfs = sorted(glob('../../PSFs/psf_vis_os045_high_nu.psf'))
)


#top.split(ByKeyword('BAND'))
mesgroup = MeasurementGroup(top)
set_max_iterations(250)
constant_background = 0.0
MAG_ZEROPOINT = 23.9


# disk radius [pix] plus a prior on the size distribution
disk_radius = FreeParameter(lambda o: o.get_radius(), Range(lambda v, o: (.5 * v, 10. * v), RangeType.EXPONENTIAL))
X_disk_radius = DependentParameter(lambda r: np.log(r), disk_radius)
add_prior(X_disk_radius, 0.4, 0.45)
# disk ratio plus a prior on the distribution
disk_ratio = FreeParameter(lambda o: o.get_aspect_ratio(), Range((0.1, 1.0), RangeType.EXPONENTIAL))
#X_disk_ratio = DependentParameter(lambda r: (1.-r)/(1.+r), disk_ratio)
#add_prior(X_disk_ratio, 0.23, 0.2)
X_disk_ratio = DependentParameter(lambda r: np.log((r-0.01)/(0.99-r)), disk_ratio)
add_prior(X_disk_ratio, 0.03, 1.0)

# sersic index [pix] plus a strong prior
sersic = FreeParameter(1.0, Range((0.3, 5.5), RangeType.LINEAR))
add_prior( sersic, 4.0, 0.2)
# sersic radius [pix] plus a prior on the size distribution
sersic_radius = FreeParameter(lambda o: o.get_radius(), Range(lambda v, o: (.05 * v, 5. * v), RangeType.EXPONENTIAL))
X_rel_size = DependentParameter( lambda x,y : np.log10(y)-(2*np.log10(x)-0.48) , disk_radius, sersic_radius) 
add_prior(X_rel_size, -0.8, 0.5)
# sersic ratio plus a prior on the distribution
sersic_ratio = FreeParameter(0.7, Range((0.1, 1.0), RangeType.EXPONENTIAL))
X_sersic_ratio = DependentParameter(lambda r: np.log((r-0.15)/(0.85-r)), sersic_ratio)
add_prior(X_sersic_ratio, 0.35, 1.6)

angle = FreeParameter(lambda o: o.get_angle())
angle_deg = DependentParameter(lambda x: np.fmod(x,np.pi/2.0)/np.pi*180.0, angle)

flux_total = get_flux_parameter()
x,y = get_pos_parameters()
ra,dec = get_world_position_parameters(x, y)

sersic_fract = FreeParameter(0.5, Range((1.0e-03,1.0), RangeType.LINEAR))
flux_sersic = DependentParameter(lambda f, r: f*r, flux_total, sersic_fract)
flux_disk = DependentParameter(lambda f, r: f*(1.0-r), flux_total, sersic_fract)
X_sersic_fract =  DependentParameter(lambda bf: np.log((bf+0.000001)/(1.01-bf)), sersic_fract)
add_prior(X_sersic_fract, -2.8, 2.1)
mag = DependentParameter(lambda f: -2.5 * np.log10(f) + MAG_ZEROPOINT, flux_total)
add_model(mesgroup, ExponentialModel(x, y, flux_disk, disk_radius, disk_ratio, angle))
add_model(mesgroup, SersicModel(x, y, flux_sersic, sersic_radius, sersic_ratio, angle, sersic))

add_output_column('x', x)
add_output_column('y', y)
add_output_column('mag', mag)
add_output_column('sersic', sersic)
add_output_column('st', sersic_fract)
add_output_column('disk_effR_px', disk_radius)
add_output_column('sersic_effR_px', sersic_radius)
add_output_column('angle', angle)
add_output_column('angle_deg', angle_deg)
add_output_column('disk_axr', disk_ratio)
add_output_column('sersic_axr', sersic_ratio)

add_output_column('RA', ra)
add_output_column('Dec', dec)
add_output_column('rel_s', X_rel_size)
add_output_column('X_st', X_sersic_fract)
add_output_column('X_rel_size', X_rel_size)
add_output_column('X_disk_radius', X_disk_radius)
add_output_column('X_disk_axr', X_disk_ratio)
add_output_column('X_sersic_axr', X_sersic_ratio)
add_output_column('flux_disk', flux_disk)
add_output_column('flux_sersic', flux_sersic)
add_output_column('flux_tot', flux_total)
