#runs the cwl that have been described thus far.
#Spews output files to this dir, should later be
# refined to usefulness
run:
	cwl-runner allByAllSimil.cwl allByAllSimil.yml
	cwl-runner placeNode.cwl placeNode.yml
	cwl-runner tmapTarOut.cwl tmapTarOut.yml
clean:
	rm mapFiles.tar *.tab *.list 
