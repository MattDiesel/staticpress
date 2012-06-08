
import shutil, os, os.path

def clean(cachepath = 'cache'):
	path = os.path.join(os.getcwd(), cachepath)

	if (os.path.exists(path)):
		shutil.rmtree(path)

	os.makedirs(path)
	print("Done.")

clean()
