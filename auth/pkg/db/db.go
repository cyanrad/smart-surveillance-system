package db

import (
	"log"

	"github.com/CCTVBackend/pkg/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func Init() *gorm.DB {
	dbURL := "postgres://pg:pass@localhost:5432/crud"

	db, err := gorm.Open(postgres.Open(dbURL), &gorm.Config{})

	if err != nil {
		log.Fatalln("err")
	}

	db.AutoMigrate(&models.Owner{}, &models.Camera{}, &models.Person{}, &models.Access{})

	return db
}
