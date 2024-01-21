from dal import IotDao

def main():
    data = IotDao.getAllTemp()

    # Affichage des données
    print("All Temperature Data:")
    for item in data:
        print(item)

if __name__ == "__main__":
    main()