from vina import Vina

v = Vina(sf_name='vina')

v.set_receptor('./data/1iep_receptor.pdbqt')

v.set_ligand_from_file('./data/1iep_ligand.pdbqt')
v.compute_vina_maps(center=[15.190, 53.903, 16.917], box_size=[20, 20, 20])
# v.compute_vina_maps(center=[17.190, 50.903, 16.917], box_size=[20, 20, 20])


# Score the current pose
energy = v.score()
print('Score before minimization: %.3f (kcal/mol)' % energy[0])

# Minimized locally the current pose
energy_minimized = v.optimize()
print('Score after minimization : %.3f (kcal/mol)' % energy_minimized[0])
v.write_pose('1iep_ligand_minimized.pdbqt', overwrite=True)

# Dock the ligand
v.dock(exhaustiveness=30, n_poses=10)

v.write_poses('1iep_ligand_vina_out.pdbqt', n_poses=10, overwrite=True)
