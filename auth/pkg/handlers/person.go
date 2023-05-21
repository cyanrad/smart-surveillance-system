package handlers

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"strconv"

	"github.com/CCTVBackend/pkg/models"
	"github.com/gorilla/mux"
)

func (h handler) CreatePerson(w http.ResponseWriter, r *http.Request) {

	//Read request body
	defer r.Body.Close()
	body, err := io.ReadAll(r.Body)

	if err != nil {
		log.Fatalln(err)
	}

	var person models.Person
	json.Unmarshal(body, &person)

	//add to database and check if error
	if result := h.DB.Create(&person); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Return status Created
	w.WriteHeader(http.StatusCreated)
	w.Header().Add("Content-Type", "application/json")
	data, err := json.Marshal(person)
	if err != nil {
		log.Println(err)
	}
	w.Write(data)
}

func (h handler) ReadPerson(w http.ResponseWriter, r *http.Request) {

	//Get id from URL
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	var person models.Person
	// find person in db
	if result := h.DB.First(&person, id); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Return status Created
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode(person)
}

func (h handler) UpdatePerson(w http.ResponseWriter, r *http.Request) {
	//Get Id from URL,
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	//Read request body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		log.Fatalln(err)
	}

	var person models.Person
	//Find person in DB
	result := h.DB.First(&person, id)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Overwrite person data
	var newPerson models.Person
	json.Unmarshal(body, &newPerson)
	person = newPerson

	//make sure id doesnt change (to avoid dupes)
	person.ID = uint64(id)

	//Push changes to DB
	h.DB.Save(&person)

	//return ok
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Updated")

}
func (h handler) DeletePerson(w http.ResponseWriter, r *http.Request) {

	//Get Id from URL,
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	var person models.Person

	//Find person in DB
	result := h.DB.First(&person, id)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Delete person in DB
	if result := h.DB.Delete(&person); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//return ok
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Deleted")
}
