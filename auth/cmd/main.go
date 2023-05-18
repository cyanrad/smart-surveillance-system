package main

import (
	"log"
	"net/http"

	"github.com/CCTVBackend/pkg/db"
	"github.com/CCTVBackend/pkg/handlers"
	"github.com/gorilla/mux"
)

func main() {

	DB := db.Init()
	h := handlers.New(DB)
	router := mux.NewRouter()

	//Owner CRUD
	router.HandleFunc("/createOwner", h.CreateOwner).Methods(http.MethodPost)
	router.HandleFunc("/readOwner/{id}", h.ReadOwner).Methods(http.MethodGet)
	router.HandleFunc("/updateOwner/{id}", h.UpdateOwner).Methods(http.MethodPut)
	router.HandleFunc("/deleteOwner/{id}", h.DeleteOwner).Methods(http.MethodDelete)

	//Camera CRUD
	router.HandleFunc("/createCamera", h.CreateCamera).Methods(http.MethodPost)
	router.HandleFunc("/readCamera/{id}", h.ReadCamera).Methods(http.MethodGet)
	router.HandleFunc("/updateCamera/{id}", h.UpdateCamera).Methods(http.MethodPut)
	router.HandleFunc("/deleteCamera/{id}", h.DeleteCamera).Methods(http.MethodDelete)

	//Person CRUD
	router.HandleFunc("/createPerson", h.CreatePerson).Methods(http.MethodPost)
	router.HandleFunc("/readPerson/{id}", h.ReadPerson).Methods(http.MethodGet)
	router.HandleFunc("/updatePerson/{id}", h.UpdatePerson).Methods(http.MethodPut)
	router.HandleFunc("/deletePerson/{id}", h.DeletePerson).Methods(http.MethodDelete)

	//Access CRUD
	router.HandleFunc("/createAccess", h.CreateAccess).Methods(http.MethodPost)
	router.HandleFunc("/readAccess/{cid}/{pid}", h.ReadAccess).Methods(http.MethodGet)
	router.HandleFunc("/updateAccess/{cid}/{pid}", h.UpdateAccess).Methods(http.MethodPut)
	router.HandleFunc("/deleteAccess/{cid}/{pid}", h.DeleteAccess).Methods(http.MethodDelete)

	log.Println("Api is running")
	http.ListenAndServe(":4000", router)
}
