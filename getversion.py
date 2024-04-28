import ROOT as R

def main():
    # Get and print the ROOT version
    root_version = R.gROOT.GetVersion()
    print("ROOT Version:", root_version)

if __name__ == '__main__':
    main()
